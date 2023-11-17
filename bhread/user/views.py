from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from feed import selectors as sel
from feed.forms import FeedRegisterForm, FeedUpdateForm

from .forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm


def register(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        if u_form.is_valid():
            u_form.save()
            username = u_form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}")
            return redirect("login")
    else:
        u_form = UserRegisterForm()
    return render(
        request,
        "user/register.html",
        {"u_form": u_form, "f_form": "", "base_template": "feed/base.html"},
    )


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated")
            return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "f_form": "",  # TODO: remove
        "verified": sel.user_has_verified(request.user),
        "base_template": "feed/tri-column.html",
    }

    return render(request, "user/profile.html", context)
