# -*- coding: utf-8 -*-

import os

from django.shortcuts import redirect
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from core import forms
from core.menu import menus
from core.models import Student
from core.utils import render


FORMS = [
    ('personal', forms.StudentPersonalDataForm),
    ('job', forms.StudentJobForm),
    ('apply', forms.StudentApplyForm),
]

TEMPLATES = {
    'personal': 'students/add/personal.html',
    'job': 'students/add/job.html',
    'apply': 'students/add/apply.html',
}


class StudentWizard(SessionWizardView):

    file_storage = FileSystemStorage(location=os.path.join(
        settings.MEDIA_ROOT, 'pictures'))

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kw):
        ctx = super(StudentWizard, self).get_context_data(form=form, **kw)
        _ctx = dict(page_title=_(u'Add new Student'),
            subtitle=_(u'Step: {0}/{1}'.format(self.steps.step1,
                self.steps.count)), menus=menus, dp=True, need_ajax=True)
        ctx.update(_ctx)
        return ctx

    def done(self, form_list, **kw):
        d = {}
        for form in form_list:
            for k, v in form.cleaned_data.iteritems():
                if v:
                    d[k] = v
        s = Student.objects.create(**d)
        s.save()
        return redirect('core-student-added', s.id)


student_wizard_view = StudentWizard.as_view(FORMS)


@permission_required('core.change_student')
def student_wizard_view_wrapper(req):
    return student_wizard_view(req)


def student_added(req, student_id):
    s = Student.objects.select_related().get(id=int(student_id))
    ctx = dict(page_title=_(u'New student added'), s=s, menus=menus,
        subtitle=_(u'{l}, {f}'.format(l=s.lastname, f=s.firstname)))
    return render(req, 'students/add/success.html', ctx)
