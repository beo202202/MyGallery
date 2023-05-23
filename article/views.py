from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from article.models import Article, Comment
from article.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)


class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all().order_by("-created_at")
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def put(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            article.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # ===================== 댓글 목록 보기 =========================
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        comments = article.comment.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ======================== 댓글 작성 ============================
    def post(self, request, article_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ======================== 댓글 삭제 ============================
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": "댓글 작성자만 삭제 가능."}, status=status.HTTP_403_FORBIDDEN
            )




#------------------- 게시글 좋아요 ------------------- 
# 게시글 좋아요 등록, 취소
class ArticleHeartsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
	#인증된 사용자만 접근
    def post(self, request, article_id):
        # 요청된 article_id를 가진 게시글을 찾는다.
        article = get_object_or_404(Article, id=article_id)
        try:
            articlehearts = ArticleHearts.objects.get(article=article, user=request.user)
            articlehearts.delete()
            return Response({"message": "좋아요를 취소했습니다"}, status=status.HTTP_200_OK)

        except ArticleHearts.DoesNotExist: #<- 에러가 발생했을 찾기 쉽다. 
            articlehearts = ArticleHearts.objects.create(article=article, user=request.user)
            return Response({"message": "좋아요를 눌렀습니다"}, status=status.HTTP_200_OK)


#------------------- 게시글 좋아요 갯수 ------------------- 
    def get(self, request, article_id):
        article = Article.objects.get(id=article_id)
        heart_count = article.count_hearts()
        return Response({'hearts': heart_count})



#--------------------- 게시글 좋아요 보기 ----------------------
class HeartsListView(APIView):
    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
    
        try:
            article.hearts.remove(request.user)
            return Response('좋아요 취소', status=status.HTTP_200_OK)
        except HeartsList.DoesNotExist:
            article.hearts.add(request.user)
            return Response('좋아요', status=status.HTTP_200_OK)

    def get(self, request):
        user = request.user
        article = user.hearts.all()
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
