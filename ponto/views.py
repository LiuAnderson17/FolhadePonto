from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from .models import RegistroPonto
from datetime import timedelta, datetime


def get_intervalo_dia(data):
    inicio = timezone.make_aware(datetime.combine(data, datetime.min.time()))
    fim = timezone.make_aware(datetime.combine(data, datetime.max.time()))
    return inicio, fim


@login_required
def dashboard(request):
    hoje = timezone.localdate()
    inicio, fim = get_intervalo_dia(hoje)

    registros_hoje = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__range=(inicio, fim)
    ).order_by('data_hora')

    ultimo_registro = registros_hoje.last()
    proximo_tipo = 'Saída' if ultimo_registro and ultimo_registro.tipo == 'E' else 'Entrada'

    context = {
        'registros_hoje': registros_hoje,
        'proximo_tipo': proximo_tipo,
        'hoje': hoje.strftime('%d/%m/%Y'),
    }
    return render(request, 'ponto/dashboard.html', context)


@login_required
def bater_ponto(request):
    if request.method != 'POST':
        return redirect('dashboard')

    hoje = timezone.localdate()
    inicio, fim = get_intervalo_dia(hoje)

    registros_hoje = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__range=(inicio, fim)
    ).order_by('data_hora')

    qtd_marcacoes = registros_hoje.count()

    proximo_tipo = 'Saída' if registros_hoje.last() and registros_hoje.last().tipo == 'E' else 'Entrada'

    if qtd_marcacoes >= 4:
        if hasattr(request, 'htmx') and request.htmx:
            response = render(request, 'ponto/partials/marcacoes_hoje.html', {
                'registros_hoje': registros_hoje,
                'proximo_tipo': proximo_tipo,
            })
            response['HX-Trigger'] = 'showLimitToast'
            return response

        messages.warning(request, "Você já registrou o máximo de 4 marcações hoje.")
        return redirect('dashboard')

    ultimo = registros_hoje.last()
    tipo = 'S' if ultimo and ultimo.tipo == 'E' else 'E'

    RegistroPonto.objects.create(
        usuario=request.user,
        tipo=tipo
    )

    registros_hoje = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__range=(inicio, fim)
    ).order_by('data_hora')

    proximo_tipo = 'Entrada' if tipo == 'S' else 'Saída'

    if hasattr(request, 'htmx') and request.htmx:
        return render(request, 'ponto/partials/marcacoes_hoje.html', {
            'registros_hoje': registros_hoje,
            'proximo_tipo': proximo_tipo,
        })

    return redirect('dashboard')


@login_required
def relatorio(request):
    hoje = timezone.localdate()

    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    if data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            data_inicio = data_fim = None
    else:
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = (primeiro_dia + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        data_inicio = primeiro_dia
        data_fim = ultimo_dia

    if not data_inicio or not data_fim or data_inicio > data_fim:
        primeiro_dia = hoje.replace(day=1)
        ultimo_dia = (primeiro_dia + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        data_inicio = primeiro_dia
        data_fim = ultimo_dia

    inicio = timezone.make_aware(datetime.combine(data_inicio, datetime.min.time()))
    fim = timezone.make_aware(datetime.combine(data_fim, datetime.max.time()))

    registros_periodo = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__range=(inicio, fim)
    ).order_by('data_hora')

    dias = {}
    for reg in registros_periodo:
        dia = timezone.localtime(reg.data_hora).date()
        if dia not in dias:
            dias[dia] = []
        dias[dia].append(reg)

    jornada_esperada = timedelta(hours=8)

    relatorio_dias = []
    saldo_acumulado = timedelta(0)

    for dia, regs in sorted(dias.items()):
        tempo_trabalhado = timedelta(0)
        intervalo_real = timedelta(0)
        tem_intervalo = False
        saldo_dia = timedelta(0)
        status = 'incompleto'

        if len(regs) >= 2:
            for i in range(0, len(regs) - 1, 2):
                entrada = regs[i].data_hora
                saida = regs[i+1].data_hora
                tempo_trabalhado += saida - entrada

            if len(regs) == 4:
                intervalo_real = regs[2].data_hora - regs[1].data_hora
                tem_intervalo = intervalo_real > timedelta(0)

            saldo_dia = tempo_trabalhado - jornada_esperada
            status = 'positivo' if saldo_dia > timedelta(0) else 'negativo' if saldo_dia < timedelta(0) else 'zerado'
            saldo_acumulado += saldo_dia

        relatorio_dias.append({
            'dia': dia,
            'marcações': regs,
            'tempo_trabalhado': tempo_trabalhado,
            'intervalo_real': intervalo_real,
            'saldo_dia': saldo_dia,
            'status': status,
            'tem_intervalo': tem_intervalo,
        })

    total_seconds = saldo_acumulado.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int(abs(total_seconds % 3600 // 60))
    sign = '+' if total_seconds >= 0 else '-'
    saldo_acumulado_str = f"{sign}{abs(hours)}h {minutes:02}min"

    context = {
        'mes_ano': hoje.strftime('%B/%Y').capitalize(),
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'periodo_str': f"de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        'relatorio_dias': relatorio_dias,
        'saldo_acumulado': saldo_acumulado,
        'saldo_acumulado_str': saldo_acumulado_str,
        'saldo_acumulado_class': 'text-success' if total_seconds >= 0 else 'text-danger',
        'hoje': hoje,
    }

    return render(request, 'ponto/relatorio.html', context)
