from django.contrib import admin
from django.utils import timezone
from .models import RegistroPonto

@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'get_tipo_display',
        'data_hora',
        'dia'  # vamos adicionar um método para mostrar só a data
    )
    list_filter = ('usuario', 'data_hora')          # ← corrigido: só o campo data_hora
    search_fields = ('usuario__username', 'usuario__first_name')
    date_hierarchy = 'data_hora'                    # permite filtrar por data no topo
    ordering = ('-data_hora',)
    #readonly_fields = ('data_hora',)

    # Método auxiliar para mostrar só a data no list_display
    def dia(self, obj):
        return obj.data_hora.date()
    dia.short_description = 'Data'

    def get_tipo_display(self, obj):
        return obj.get_tipo_display()
    get_tipo_display.short_description = 'Tipo'