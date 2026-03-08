from django.contrib import admin
from django.utils import timezone
from .models import RegistroPonto


@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'get_tipo_marcacao_display',
        'posicao',                  # posição no turno (1 a 4)
        'data_hora',
        'dia',
        'data_referencia',          # data do agrupamento/turno
    )
    list_display_links = ('usuario', 'data_hora')  # clica nesses pra editar o registro
    list_filter = (
        'usuario',
        'data_referencia',          # filtro por data de referência
        'tipo_marcacao',
    )
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
    )
    date_hierarchy = 'data_referencia'  # filtro por mês/ano no topo (baseado na data_referencia)
    ordering = ('-data_referencia', '-posicao', '-data_hora')

    # Método auxiliar para mostrar só a data civil
    def dia(self, obj):
        return obj.data_hora.date()
    dia.short_description = 'Data Civil'

    # Exibe o nome bonito da etapa (Entrada Inicial, Saída para Almoço, etc.)
    @admin.display(description='Etapa da Jornada')
    def get_tipo_marcacao_display(self, obj):
        return obj.get_tipo_marcacao_display()