from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class RegistroPonto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(
        max_length=1,
        choices=[('E', 'Entrada'), ('S', 'Saída')],
        default='E'
    )

    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    def get_tipo_display(self):
        return dict(self._meta.get_field('tipo').choices)[self.tipo]