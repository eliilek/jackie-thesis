from django.db import models
from django.urls import reverse
from django.utils import timezone

class Phase(models.Model):
    phase_num = models.SmallIntegerField(verbose_name="Phase Number")
    passing_accuracy_percentage = models.SmallIntegerField(null=True, blank=True, verbose_name="Passing Accuracy % (Do not use with count)")
    passing_correct_count = models.SmallIntegerField(null=True, blank=True, verbose_name="Correct Responses For Passing (Do not use with %)")
    passing_time = models.DurationField(null=True, blank=True, verbose_name="Passing Time (ms)")
    ordering = models.SmallIntegerField(verbose_name="Ordering # - lowest numbered phase appears first")
    feedback = models.BooleanField(default=True)
    fail_phase = models.ForeignKey('self', verbose_name="Phase to redirect to if failed too many times", on_delete=models.SET_NULL, null=True, blank=True)
    fail_limit = models.SmallIntegerField(default=0, verbose_name="Number of allowed failures before redirect")
    disable_fail_limit = models.SmallIntegerField(default=0, verbose_name="Total allowed failures before deactivation")

    def __unicode__(self):
        return "Phase " + str(self.phase_num)

    def get_passing_time(self):
        return self.response_time.microseconds/1000.0

class Group(models.Model):
    name = models.CharField(max_length=10)
    phases = models.ManyToManyField(Phase)

    def __unicode__(self):
        return "Group " + self.name

class Subject(models.Model):
    subject_id = models.SmallIntegerField(primary_key=True)
    phase = models.ForeignKey(Phase, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("subject", args=[str(self.id)])

    def __unicode__(self):
        return "Subject " + str(self.subject_id)

class Failure(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phase, on_delete=models.SET_NULL, null=True)
    times_failed = models.SmallIntegerField(default=0)

class Symbol(models.Model):
    name = models.CharField(max_length=50)
    symbol_text = models.CharField(max_length=10, verbose_name="Text to Display")
    font_family = models.CharField(max_length=50, verbose_name="Font Family (blank for default)", default="Arial")

    def __unicode__(self):
        return self.name

class SingleSet(models.Model):
    class Meta:
        verbose_name = "Single Set"
    stimulus = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    option_1 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="first")
    option_2 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="second")
    option_3 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="third")
    correct_response = models.CharField(max_length=1, verbose_name="Option Number of Correct Response (1, 2, or 3)")
    frequency = models.SmallIntegerField(verbose_name="Times to appear per condition")
    phases = models.ManyToManyField(Phase)

class ResponseBlock(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    phase = models.ForeignKey(Phase, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(ResponseBlock, self).save(*args, **kwargs)

    def date_time(self):
        return self.created

    def get_absolute_url(self):
        return reverse("response_set", args=[str(self.id)])

    def successful(self):
        responses = self.response_set.all()
        time = 0
        correct = 0
        count = 0
        for response in responses:
            time += response.get_response_time()
            count += 1
            correct += response.correct()

        if (not self.phase.passing_accuracy_percentage) or (correct/count >= self.phase.passing_accuracy_percentage/100):
            if (not self.phase.passing_time) or (time <= self.phase.passing_time):
                if (not self.phase.passing_correct_count) or (correct >= self.phase.passing_correct_count and self.phase.passing_correct_count >= 0) or (self.phase.passing_correct_count < 0 and correct <= self.phase.passing_correct_count):
                    return "Passed"
        return "Failed"

class Response(models.Model):
    block = models.ForeignKey(ResponseBlock, on_delete=models.CASCADE)
    response_time = models.DurationField(null=True)
    stimulus = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    option_1 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="first_response")
    option_2 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="second_response")
    option_3 = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name="third_response")
    correct_response = models.PositiveSmallIntegerField()
    given_response = models.PositiveSmallIntegerField(null=True)

    def get_response_time(self):
        try:
            return self.response_time.microseconds/1000.0
        except:
            return 0

    def correct(self):
        if self.correct_response == self.given_response:
            return 1
        return 0

class SessionLength(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    trials = models.SmallIntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(SessionLength, self).save(*args, **kwargs)
