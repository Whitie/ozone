from django.contrib import admin
from ozone.feedback.models import *

# Register your models here.

admin.site.register(Question)
admin.site.register(QuestionSet)
admin.site.register(QuestionExtra)
admin.site.register(Feedback)
admin.site.register(FeedbackToken)
admin.site.register(Answer)
