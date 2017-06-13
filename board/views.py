from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm


class IndexView(TemplateView):
    """Main view for the eventual single page app."""
    template_name = 'board/index.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(request)


class Signup(FormView):
    """Signup a new user to the site."""
    template_name = 'board/signup.html'
    form_class = UserCreationForm
    def get(self, request, *args, **kwargs):
        """Show the signup form."""
        form = self.get_form(self.form_class)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Handle the submitted form."""
        form = self.get_form(self.form_class)
        # add the email address
        if form.is_valid():
            form.save()
            # log the user in
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
