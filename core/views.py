from django.views.generic import TemplateView


class DemoFormView(TemplateView):
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class LoginView(DemoFormView):
    template_name = 'core/login.html'


class SignupView(DemoFormView):
    template_name = 'core/signup.html'


class ProfileView(DemoFormView):
    template_name = 'core/profile.html'
    extra_context = {'show_profile_menu': True}
