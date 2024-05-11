import json
import graphene
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import DatabaseError, IntegrityError
from django.db.models import Q
from django.db.transaction import atomic
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from blog.posts.models import Category, Post


class CategoryType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()
    post_count = graphene.Int(exclude_subcategories=graphene.Boolean())
    subcategories = graphene.List(lambda: CategoryType)
    cover_image = graphene.String()

    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_name(self, info):
        if self.id is None:
            return "전체 게시글"

        if self.id == 0:
            return "분류 미지정"

        return self.name

    @staticmethod
    def resolve_description(self, info):
        if self.id is None:
            return "블로그의 모든 게시글"

        if self.id == 0:
            return "분류가 없는 게시글"

        return self.description

    @staticmethod
    def resolve_subcategories(self, info):
        if not info.context.user.is_authenticated:
            self.subcategories.exclude(is_hidden=True)
        return self.subcategories.all()

    @staticmethod
    def resolve_post_count(self, info, exclude_subcategories=False):
        posts = Post.objects.exclude(Q(is_deleted=True) | Q(category__is_deleted=True))

        if not info.context.user.is_authenticated:
            posts = posts.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))

        if self.id is None:
            pass
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            if exclude_subcategories:
                posts = self.posts
            else:
                posts = Post.objects.filter(category__in=Category.get_descendants(self, include_self=True),
                                            category__is_deleted=False)

        return posts.count()

    @staticmethod
    def resolve_posts(self, info):
        if self.id is None:
            posts = Post.objects.all()
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            posts = self.posts.all()

        posts = posts.exclude(is_deleted=True)
        if not info.context.user.is_authenticated:
            posts = posts.exclude(is_hidden=True)

        return posts

    @staticmethod
    def resolve_cover_image(self, info):
        return self.cover_image.url if self.cover_image else None


class PostType(DjangoObjectType):
    category = graphene.Field(CategoryType)

    class Meta:
        model = Post
        fields = '__all__'

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType)
    category_list = graphene.JSONString()
    valid_supercategories = graphene.List(CategoryType, id=graphene.Int(required=True))
    category_info = graphene.Field(CategoryType, id=graphene.Int())
    post_list = graphene.List(PostType, category_id=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_categories(root, info):
        if not info.context.user.is_authenticated:
            return Category.objects.exclude(is_hidden=True)

        return Category.objects.all()

    @staticmethod
    def resolve_category_list(root, info):
        authenticated = info.context.user.is_authenticated
        root_categories = Category.objects.root_nodes().filter(is_deleted=False)
        all_posts = Post.objects.exclude(Q(is_deleted=True)|Q(category__is_deleted=True))

        if not authenticated:
            root_categories = root_categories.exclude(is_hidden=True)
            all_posts = all_posts.exclude(Q(category__is_hidden=True) | Q(is_hidden=True))

        def category_to_dict(instance):
            subcategories = instance.subcategories.filter(is_deleted=False)

            if not authenticated:
                subcategories = subcategories.exclude(is_hidden=True)

            result = {
                'id': instance.id,
                'isHidden': instance.is_hidden,
                'name': instance.name,
                'postCount': all_posts.filter(category__in=instance.get_descendants(include_self=True)).count(),
                'subcategories': [category_to_dict(subcategory)
                                  for subcategory in subcategories]
            }
            return result

        categories_list = [{
            'name': '전체 게시글',
            'postCount': all_posts.count(),
            'subcategories': []
        }]
        categories_list.extend([category_to_dict(category) for category in root_categories])
        categories_list.append({
            'id': 0,
            'name': '분류 미지정',
            'postCount': all_posts.filter(category__isnull=True).count(),
            'subcategories': []
        })
        return json.dumps(categories_list)


    @login_required
    @staticmethod
    def resolve_valid_supercategories(root, info, **args):
        id = args.get('id')
        result = Category.objects.filter(id=id).first()

        return Category.objects.exclude(Q(id__in=result.get_descendants(include_self=True))|Q(is_deleted=True))


    @staticmethod
    def resolve_category_info(root, info, **args):
        id = args.get('id')

        if id is None:
            return Category()

        if id == 0:
            return Category(id=0)

        result = Category.objects.filter(id=id).first()

        if not info.context.user.is_authenticated and result.is_hidden:
            raise GraphQLError('You do not have permission to perform this action')

        return result

    @staticmethod
    def resolve_post_list(root, info, **args):
        authenticated = info.context.user.is_authenticated
        category_id = args.get('category_id')

        posts = Post.objects.exclude(Q(is_deleted=True) | Q(category__is_deleted=True))

        if not authenticated:
            posts = posts.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))

        if category_id is None:
            pass
        elif category_id == 0:
            posts = posts.filter(category__isnull=True)
        else:
            try:
                category = Category.objects.get(id=category_id)
                if not authenticated and category.is_hidden:
                    raise GraphQLError('You do not have permission to perform this action')
            except Category.DoesNotExist:
                return []

            subcategories = category.get_descendants(include_self=True)
            posts = posts.filter(category__in=subcategories)

        return posts

    @staticmethod
    def resolve_post(root, info, **args):
        try:
            post = Post.objects.get(id=args.get('id'))
        except Post.DoesNotExist:
            return None

        if not info.context.user.is_authenticated and \
                (post.is_hidden or (post.category is not None and post.category.is_hidden)):
            raise GraphQLError('You do not have permission to perform this action')

        return post


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    cover_image = Upload()
    subcategory_of = graphene.Int()


class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        data = CategoryInput(required=True)

    success = graphene.Boolean()
    created_category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        data = args.get('data')

        if 'subcategory_of' in data:
            try:
                supercategory = Category.objects.get(id=data.subcategory_of)
            except Category.DoesNotExist:
                raise GraphQLError(f'Category with id {data.subcategory_of} does not exist.')
        else:
            supercategory = None

        try:
            category = Category.objects.create(name=data.name,
                                               description=data.description,
                                               is_hidden=data.is_hidden,
                                               cover_image=data.cover_image,
                                               subcategory_of=supercategory)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create category: {e}')

        return CreateCategoryMutation(success=True, created_category=category)


class UpdateCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = CategoryInput(required=True)

    success = graphene.Boolean()
    updated_category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    @atomic
    def mutate(root, info, **args):
        category_id = args.get('id')

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return UpdateCategoryMutation(success=False, updated_category=None)

        data = args.get('data')
        category.name = data.get('name')
        if 'subcategory_of' in data:
            try:
                category.subcategory_of = Category.objects.get(id=data.subcategory_of)
            except Category.DoesNotExist:
                raise GraphQLError(f'Category with id {data.subcategory_of} does not exist.')
        else:
            category.subcategory_of = None
        category.description = data.get('description')
        is_hidden = data.get('is_hidden')
        if is_hidden and not category.is_hidden:
            category.get_descendants().update(is_hidden=True)
        category.is_hidden = is_hidden

        if 'cover_image' in data:
            cover_image = data.get('cover_image')
            if cover_image is None:
                category.cover_image.delete()
            else:
                content_file = ContentFile(cover_image.read())
                category.cover_image.save(cover_image.name, content_file, save=True)

        try:
            category.save()
        except (DatabaseError, IntegrityError) as e:
            return UpdateCategoryMutation(success=False, updated_category=None)

        return UpdateCategoryMutation(success=True, updated_category=category)


class DeleteCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @atomic
    @login_required
    def mutate(self, info, **args):
        category_id = args.get('id')

        try:
            category = Category.objects.get(id=category_id)
            category.get_descendants().update(is_deleted=True)
            category.is_deleted = True
            category.save()
            return DeleteCategoryMutation(success=True)
        except Category.DoesNotExist:
            raise GraphQLError(f'Post with id {category_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(f'Failed to delete category with id {category_id}')


class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=False)
    content = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    thumbnail = graphene.String(required=False)


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        data = PostInput(required=True)

    success = graphene.Boolean()
    created_post = graphene.Field(PostType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        data = args.get('data')

        if 'category' in data:
            try:
                category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                raise GraphQLError(f'Category with id {data.category} does not exist.')
        else:
            category = None

        try:
            post = Post.objects.create(title=data.title,
                                       category=category,
                                       content=data.content,
                                       is_hidden=data.is_hidden,
                                       thumbnail=data.thumbnail)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create post: {e}')

        return CreatePostMutation(success=True, created_post=post)


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = PostInput(required=True)

    success = graphene.Boolean()
    updated_post = graphene.Field(PostType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        post_id = args.get('id')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return UpdatePostMutation(success=False, updated_post=None)

        data = args.get('data')
        post.title = data.get('title', post.title)
        if 'category' in data:
            try:
                post.category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                raise GraphQLError(f'Category with id {data.category} does not exist.')
        else:
            post.category = None
        post.content = data.get('content', post.content)
        post.is_hidden = data.get('is_hidden', post.is_hidden)
        post.thumbnail = data.get('thumbnail', post.thumbnail)

        try:
            post.save()
        except (DatabaseError, IntegrityError) as e:
            return UpdatePostMutation(success=False, updated_post=None)

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        post_id = args.get('id')

        try:
            post = Post.objects.get(id=post_id)
            post.is_deleted = True
            post.save()
            return DeletePostMutation(success=True)
        except Post.DoesNotExist:
            raise GraphQLError(f'Post with id {post_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(f'Failed to delete post with id {post_id}')


class UploadImageMutation(graphene.Mutation):
    class Arguments:
        files = graphene.List(Upload, required=True)

    urls = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        files = args.get('files')

        urls = []
        for file in files:
            path = default_storage.save(f'media/{file.name}', ContentFile(file.read()))
            urls.append(default_storage.url(path))


class Mutation(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
    upload_image = UploadImageMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
