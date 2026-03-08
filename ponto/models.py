from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class RegistroPonto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(default=timezone.now)
    tipo_marcacao = models.CharField(
        max_length=2,
        choices=[
            ('E1', 'Entrada Inicial'),
            ('S1', 'Saída para Almoço'),
            ('E2', 'Volta do Almoço'),
            ('S2', 'Fim da Jornada'),
        ],
        default='E1'
    )
    data_referencia = models.DateField(null=True, blank=True, editable=False)
    posicao = models.PositiveSmallIntegerField(default=1, editable=False)  # 1 a 4

    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['data_referencia', 'posicao', '-data_hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_marcacao_display()} - {self.data_hora.strftime('%d/%m/%Y %H:%M')} (pos {self.posicao})"

    def get_tipo_marcacao_display(self):
        return dict(self._meta.get_field('tipo_marcacao').choices).get(self.tipo_marcacao, self.tipo_marcacao)

    def save(self, *args, **kwargs):
        if not self.data_referencia:
            local_time = timezone.localtime(self.data_hora)
            hora = local_time.hour
            data_base = local_time.date()
            if 0 <= hora < 6:
                self.data_referencia = data_base - timedelta(days=1)
            else:
                self.data_referencia = data_base

        super().save(*args, **kwargs)