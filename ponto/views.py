from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import RegistroPonto
from datetime import timedelta, datetime
from collections import defaultdict


def get_intervalo_referencia(data_referencia):
    inicio = timezone.make_aware(datetime.combine(data_referencia, datetime.min.time()))
    fim = timezone.make_aware(datetime.combine(data_referencia, datetime.max.time())) + timedelta(days=1) - timedelta(seconds=1)
    return inicio, fim


@login_required
def dashboard(request):
    hoje = timezone.localdate()

    ultimo_registro = RegistroPonto.objects.filter(usuario=request.user).order_by('-data_hora').first()

    if ultimo_registro and ultimo_registro.data_referencia:
        # Verifica se o turno do último registro já está completo
        registros_ultimo_turno = RegistroPonto.objects.filter(
            usuario=request.user,
            data_referencia=ultimo_registro.data_referencia
        )
        if len(registros_ultimo_turno) >= 4:
            # Turno anterior fechado → usa hoje para novo turno
            data_ref_atual = hoje
        else:
            # Turno ainda aberto → continua nele
            data_ref_atual = ultimo_registro.data_referencia
    else:
        data_ref_atual = hoje

    inicio, fim = get_intervalo_referencia(data_ref_atual)

    registros_qs = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__range=(inicio, fim)
    )

    ordem_etapas = {'E1': 1, 'S1': 2, 'E2': 3, 'S2': 4}
    registros_atuais = RegistroPonto.objects.filter(
        usuario=request.user,
        data_referencia=data_ref_atual
    ).order_by('posicao')

    ultimo = registros_atuais.last() if registros_atuais.exists() else None

    # Próximo tipo
    if not ultimo:
        proximo_tipo = 'Entrada Inicial (E1)'
    else:
        ultimo_tipo = ultimo.tipo_marcacao
        if ultimo_tipo == 'E1':
            proximo_tipo = 'Saída para Almoço (S1)'
        elif ultimo_tipo == 'S1':
            proximo_tipo = 'Volta do Almoço (E2)'
        elif ultimo_tipo == 'E2':
            proximo_tipo = 'Fim da Jornada (S2)'
        elif ultimo_tipo == 'S2':
            proximo_tipo = 'Turno completo (próximo turno)'
        else:
            proximo_tipo = 'Entrada Inicial (E1)'

    context = {
        'registros_hoje': registros_atuais,
        'proximo_tipo': proximo_tipo,
        'hoje': hoje.strftime('%d/%m/%Y'),
        'data_referencia_display': data_ref_atual.strftime('%d/%m/%Y'),
    }
    return render(request, 'ponto/dashboard.html', context)


@login_required
def bater_ponto(request):
    if request.method != 'POST':
        return redirect('dashboard')

    agora = timezone.now()
    hoje = timezone.localdate(agora)

    ultimo = RegistroPonto.objects.filter(usuario=request.user).order_by('-data_hora').first()

    if ultimo and ultimo.posicao == 4:
        data_ref = hoje
        posicao_atual = 1
    elif ultimo:
        data_ref = ultimo.data_referencia
        posicao_atual = ultimo.posicao + 1
        if posicao_atual > 4:
            posicao_atual = 1
    else:
        data_ref = hoje
        posicao_atual = 1

    pos_to_tipo = {1: 'E1', 2: 'S1', 3: 'E2', 4: 'S2'}
    tipo_marcacao = pos_to_tipo.get(posicao_atual, 'E1')

    RegistroPonto.objects.create(
        usuario=request.user,
        tipo_marcacao=tipo_marcacao,
        data_referencia=data_ref,
        posicao=posicao_atual
    )

    registros_turno = RegistroPonto.objects.filter(
        usuario=request.user,
        data_referencia=data_ref
    ).order_by('posicao')

    if posicao_atual == 4:
        proximo_tipo = 'Turno completo'
    else:
        proximo_pos = posicao_atual + 1
        proximo_tipo = {
            1: 'Saída para Almoço (S1)',
            2: 'Volta do Almoço (E2)',
            3: 'Fim da Jornada (S2)',
            4: 'Turno completo'
        }.get(proximo_pos, 'Próxima etapa')

    if request.htmx:
        return render(request, 'ponto/partials/marcacoes_hoje.html', {
            'registros_hoje': registros_turno,
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

    registros_periodo = RegistroPonto.objects.filter(
        usuario=request.user,
        data_referencia__range=(data_inicio, data_fim)
    )

    dias = defaultdict(list)
    for reg in registros_periodo:
        dias[reg.data_referencia].append(reg)

    jornada_esperada = timedelta(hours=8)

    relatorio_dias = []
    saldo_acumulado = timedelta(0)

    ordem_etapas = {'E1': 1, 'S1': 2, 'E2': 3, 'S2': 4}

    for dia, regs in sorted(dias.items()):
        tempo_trabalhado = timedelta(0)
        intervalo_real = timedelta(0)
        tem_intervalo = False
        status = 'incompleto'
        saldo_dia = timedelta(0)

        # Ordenação lógica pela sequência da jornada
        regs_ordenados = sorted(regs, key=lambda r: ordem_etapas.get(r.tipo_marcacao, 99))

        if len(regs_ordenados) == 4:
            try:
                e1 = next(r.data_hora for r in regs_ordenados if r.tipo_marcacao == 'E1')
                s1 = next(r.data_hora for r in regs_ordenados if r.tipo_marcacao == 'S1')
                e2 = next(r.data_hora for r in regs_ordenados if r.tipo_marcacao == 'E2')
                s2 = next(r.data_hora for r in regs_ordenados if r.tipo_marcacao == 'S2')

                # Ajuste para fim da jornada no dia seguinte
                if s2 < e2:
                    s2 += timedelta(days=1)

                tempo_trabalhado = (s1 - e1) + (s2 - e2)
                intervalo_real = e2 - s1
                tem_intervalo = intervalo_real > timedelta(minutes=5)

                saldo_dia = tempo_trabalhado - jornada_esperada

                status = (
                    'positivo' if saldo_dia > timedelta(0)
                    else 'negativo' if saldo_dia < timedelta(0)
                    else 'zerado'
                )

                saldo_acumulado += saldo_dia
            except StopIteration:
                pass  # incompleto

        relatorio_dias.append({
            'dia': dia,
            'marcações': regs_ordenados,
            'tempo_trabalhado': tempo_trabalhado,
            'intervalo_real': intervalo_real,
            'saldo_dia': saldo_dia,
            'status': status,
            'tem_intervalo': tem_intervalo,
        })

    # Formatação do saldo acumulado
    total_seconds = int(saldo_acumulado.total_seconds())
    sign = '+' if total_seconds >= 0 else '-'
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    saldo_acumulado_str = f"{sign}{hours}h {minutes:02}min"

    context = {
        'mes_ano': hoje.strftime('%B/%Y').capitalize(),
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'periodo_str': f"de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        'relatorio_dias': relatorio_dias,
        'saldo_acumulado': saldo_acumulado,
        'saldo_acumulado_str': saldo_acumulado_str,
        'saldo_acumulado_class': 'text-success' if sign == '+' else 'text-danger' if sign == '-' else 'text-muted',
        'hoje': hoje,
    }

    return render(request, 'ponto/relatorio.html', context)