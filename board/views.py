import json

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
import requests

from .forms import ProfileForm
from django.conf import settings
from datetime import datetime


def pagination_links(count, pages, n):
    response = {
    'count': count,
    'pages': pages,
    'links': [{'url': '/jobs/?p=%s&n=%s' % (p, n), 'page_no': p}
              for p in range(1, pages + 1)]}
    return response


class IndexView(TemplateView):
    """Main view for the eventual single page app."""
    template_name = 'board/index.html'
    def get(self, request, *args, **kwargs):
        n = request.GET.get('n', 10)
        p = request.GET.get('p', 1)
        if request.user.is_authenticated():
            techs = request.user.profile.required_techs.all()
            exclude = request.user.profile.excluded_techs.all()
            techs = ','.join(tech.name for tech in techs)
            exclude = ','.join(tech.name for tech in exclude)
        else:
            techs, exclude = '', ''
        res = requests.get('%s:%s/api/v1/jobs/' % (
                settings.JOBS_API['HOST'],
                settings.JOBS_API['PORT']),
            params={'n': n, 'p': p, 'techs': techs, 'exclude': exclude})
        result = json.loads(res.json())
        context = self.get_context_data(**kwargs)
        context['pagination'] = pagination_links(
            result['count'], result['pages'], n)
        jobs = result['jobs']
        for job in jobs:
            job['date_added'] = parse_prefix(
                job['date_added'], "%Y-%m-%dT%H:%M:%S")
            job['date_posted'] = parse_prefix(
                job['date_posted'], "%Y-%m-%dT%H:%M:%S")
            job['technologies'] = sorted(list(set(job['technologies'])))
        context['jobs'] = jobs
        return self.render_to_response(context)


def parse_prefix(line, fmt):
    try:
        t = datetime.strptime(line, fmt)
    except ValueError as v:
        flag = 'unconverted data remains: '
        if len(v.args) > 0 and v.args[0].startswith(flag):
            line = line[:-(len(v.args[0]) - len(flag))]
            t = datetime.strptime(line, fmt)
        else:
            raise
    return t


class SignupView(FormView):
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


class ProfileView(LoginRequiredMixin, FormView):
    """Edit the profile for a user."""
    template_name = 'board/profile.html'
    form_class = ProfileForm
    def get(self, request, *args, **kwargs):
        """Show the profile form."""
        form = self.get_form(self.form_class)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['user'] = request.user
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Handle the submitted form."""
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return self.form_valid(profile_form)
        else:
            print(profile_form.errors)
            return self.form_invalid(profile_form, **kwargs)
