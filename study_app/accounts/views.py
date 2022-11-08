from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import CustomUser, Connection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import User, Connection
from .helpers import get_current_user

"""フォロー"""
@login_required
def follow_view(request, *args, **kwargs):
    try:
        # request.user.username = ログインユーザーのユーザー名を渡す。
        follower = CustomUser.objects.get(username=request.user.username)
        #kwargs['username'] = フォロー対象のユーザー名を渡す。
        following = CustomUser.objects.get(username=kwargs['username'])
    # 例外処理：もしフォロー対象が存在しない場合、警告文を表示させる。
    except CustomUser.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['username'])) #（※1）（※2）
        return HttpResponseRedirect(reverse_lazy('pento_app:index'))
    # フォローしようとしている対象が自分の場合、警告文を表示させる。
    if follower == following:
        messages.warning(request, '自分自身はフォローできません')
    else:
        # フォロー対象をまだフォローしていなければ、DBにフォロワー(自分)×フォロー(相手)という組み合わせで登録する。
        # createdにはTrueが入る
        _, created = Connection.objects.get_or_create(follower=follower, following=following) #（※3）

        # もしcreatedがTrueの場合、フォロー完了のメッセージを表示させる。
        if (created):
            messages.success(request, '{}をフォローしました'.format(following.username))
        # 既にフォロー相手をフォローしていた場合、createdにはFalseが入る。
        # フォロー済みのメッセージを表示させる。
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('pento_app:detail', kwargs={'username': following.username}))

"""フォロー解除"""
@login_required
def unfollow_view(request, *args, **kwargs):
    try:
        follower = CustomUser.objects.get(username=request.user.username)
        following = CustomUser.objects.get(username=kwargs['username'])
        if follower == following:
            messages.warning(request, '自分自身のフォローを外せません')
        else:
            unfollow = Connection.objects.get(follower=follower, following=following)
            # フォロワー(自分)×フォロー(相手)という組み合わせを削除する。
            unfollow.delete()
            messages.success(request, 'あなたは{}のフォローを外しました'.format(following.username))
    except CustomUser.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['username']))
        return HttpResponseRedirect(reverse_lazy('pento_app:index'))
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('pento_app:detail', kwargs={'username': following.username}))

# プロフィール画面
class ProifileDetail(LoginRequiredMixin, generic.DetailView):
    model = CustomUser
    template_name = 'detail.html'

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs): # ※(1)
        context = super(ProifileDetail, self).get_context_data(**kwargs)
        username = self.kwargs['username']
        context['username'] = username
        context['user'] = get_current_user(self.request) # ※(2)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()

        if username is not context['user'].username:
            result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
            context['connected'] = True if result else False

        return context
