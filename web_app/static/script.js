// ==================== VARIÁVEIS GLOBAIS ====================
let user = null;

// ==================== FORMATAÇÃO DE DATAS EM PORTUGUÊS ====================
function formatarDataHoraPT(dataHora) {
    const data = new Date(dataHora);
    const opcoesData = { day: '2-digit', month: '2-digit', year: 'numeric' };
    const opcoesHora = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    const dataFormatada = data.toLocaleDateString('pt-BR', opcoesData);
    const horaFormatada = data.toLocaleTimeString('pt-BR', opcoesHora);
    return { data: dataFormatada, hora: horaFormatada };
}

function formatarDataPT(dataHora) {
    const data = new Date(dataHora);
    return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatarHoraPT(dataHora) {
    const data = new Date(dataHora);
    return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function obterDiaSemanaPT(dataHora) {
    const data = new Date(dataHora);
    const dias = {
        'Sunday': 'Domingo', 'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado'
    };
    const diaIngles = data.toLocaleDateString('en-US', { weekday: 'long' });
    return dias[diaIngles];
}

function formatarDataCompletaPT(dataHora) {
    const data = new Date(dataHora);
    const diaSemana = obterDiaSemanaPT(dataHora);
    const dia = data.getDate().toString().padStart(2, '0');
    const mes = (data.getMonth() + 1).toString().padStart(2, '0');
    const ano = data.getFullYear();
    const hora = data.getHours().toString().padStart(2, '0');
    const minuto = data.getMinutes().toString().padStart(2, '0');
    return `${diaSemana}, ${dia}/${mes}/${ano} às ${hora}:${minuto}`;
}

// ==================== FUNÇÕES AUXILIARES ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getAvatarIcon(tipo) {
    const icons = { 'morador': '👨‍👩‍👧', 'visitante': '👥', 'entregador': '📦', 'tecnico': '🔧' };
    return icons[tipo] || '👤';
}

function getTipoIcon(tipo) {
    const icons = { 'morador': '🏠', 'visitante': '👥', 'entregador': '📦', 'tecnico': '🔧' };
    return icons[tipo] || '📌';
}

// ==================== FORMATAÇÃO DE TELEFONE E DOCUMENTO ====================
function formatarTelefone(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length === 0) { input.value = ''; return; }
    if (valor.length <= 2) { input.value = `(${valor}`; }
    else if (valor.length <= 7) { input.value = `(${valor.substring(0, 2)}) ${valor.substring(2)}`; }
    else if (valor.length <= 10) { input.value = `(${valor.substring(0, 2)}) ${valor.substring(2, 6)}-${valor.substring(6)}`; }
    else { input.value = `(${valor.substring(0, 2)}) ${valor.substring(2, 7)}-${valor.substring(7, 11)}`; }
}

function formatarDocumento(input) {
    let valor = input.value.replace(/\D/g, '');
    let statusSpan = document.getElementById('documentoStatus');
    if (valor.length === 0) { input.value = ''; if (statusSpan) statusSpan.style.display = 'none'; return; }
    if (valor.length <= 11) {
        if (valor.length <= 3) { input.value = valor; }
        else if (valor.length <= 6) { input.value = `${valor.substring(0, 3)}.${valor.substring(3)}`; }
        else if (valor.length <= 9) { input.value = `${valor.substring(0, 3)}.${valor.substring(3, 6)}.${valor.substring(6)}`; }
        else { input.value = `${valor.substring(0, 3)}.${valor.substring(3, 6)}.${valor.substring(6, 9)}-${valor.substring(9, 11)}`; }
        if (valor.length === 11 && statusSpan) {
            if (validarCPF(valor)) { statusSpan.innerHTML = '✅ CPF válido'; statusSpan.style.color = 'green'; statusSpan.style.display = 'inline'; }
            else { statusSpan.innerHTML = '❌ CPF inválido'; statusSpan.style.color = 'red'; statusSpan.style.display = 'inline'; }
        } else if (statusSpan) { statusSpan.style.display = 'none'; }
    } else {
        if (valor.length <= 2) { input.value = valor; }
        else if (valor.length <= 5) { input.value = `${valor.substring(0, 2)}.${valor.substring(2)}`; }
        else if (valor.length <= 8) { input.value = `${valor.substring(0, 2)}.${valor.substring(2, 5)}.${valor.substring(5)}`; }
        else { input.value = `${valor.substring(0, 2)}.${valor.substring(2, 5)}.${valor.substring(5, 8)}-${valor.substring(8, 9)}`; }
        if (statusSpan) statusSpan.style.display = 'none';
    }
}

function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    let soma = 0;
    for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i);
    let resto = 11 - (soma % 11);
    let digito1 = resto === 10 || resto === 11 ? 0 : resto;
    if (digito1 !== parseInt(cpf.charAt(9))) return false;
    soma = 0;
    for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i);
    resto = 11 - (soma % 11);
    let digito2 = resto === 10 || resto === 11 ? 0 : resto;
    if (digito2 !== parseInt(cpf.charAt(10))) return false;
    return true;
}

function limparFormatacao(valor) {
    if (!valor) return '';
    return valor.replace(/\D/g, '');
}

function formatarTelefoneExibicao(telefone) {
    if (!telefone) return '-';
    const numeros = telefone.replace(/\D/g, '');
    if (numeros.length === 10) return `(${numeros.substring(0, 2)}) ${numeros.substring(2, 6)}-${numeros.substring(6)}`;
    if (numeros.length === 11) return `(${numeros.substring(0, 2)}) ${numeros.substring(2, 7)}-${numeros.substring(7)}`;
    return telefone;
}

function formatarDocumentoExibicao(documento) {
    if (!documento) return '-';
    const numeros = documento.replace(/\D/g, '');
    if (numeros.length === 11) return `${numeros.substring(0, 3)}.${numeros.substring(3, 6)}.${numeros.substring(6, 9)}-${numeros.substring(9)}`;
    if (numeros.length <= 9) {
        if (numeros.length <= 2) return numeros;
        if (numeros.length <= 5) return `${numeros.substring(0, 2)}.${numeros.substring(2)}`;
        if (numeros.length <= 8) return `${numeros.substring(0, 2)}.${numeros.substring(2, 5)}.${numeros.substring(5)}`;
        return `${numeros.substring(0, 2)}.${numeros.substring(2, 5)}.${numeros.substring(5, 8)}-${numeros.substring(8)}`;
    }
    return documento;
}

// ==================== LOGIN ====================
async function fazerLogin() {
    const login = document.getElementById('login').value;
    const senha = document.getElementById('senha').value;
    if (!login || !senha) { alert('Preencha usuário e senha!'); return; }
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, senha })
        });
        const data = await response.json();
        if (data.success) {
            user = data.user;
            document.getElementById('userName').innerText = user.nome;
            document.getElementById('userType').innerText = user.tipo.toUpperCase();
            document.getElementById('loginScreen').classList.remove('active');
            document.getElementById('mainScreen').classList.add('active');
            const isMaster = user.tipo === 'master';
            document.querySelectorAll('.master-only').forEach(el => el.style.display = isMaster ? 'flex' : 'none');
            await carregarEstatisticas();
            await carregarPessoas();
            await carregarRegistros();
            await carregarAvisos();
            await carregarOcorrencias();
            if (isMaster) {
                await carregarPorteiros();
                await carregarCondominios();
                await carregarCondominiosParaSelect();
            }
        } else { alert(data.error); }
    } catch (error) { alert('Erro ao conectar!'); }
}

async function fazerLogout() {
    await fetch('/api/logout', { method: 'POST' });
    user = null;
    document.getElementById('mainScreen').classList.remove('active');
    document.getElementById('loginScreen').classList.add('active');
}

// ==================== PESSOAS ====================
async function carregarPessoas() {
    const busca = document.getElementById('searchPessoa')?.value || '';
    const lista = document.getElementById('listaPessoas');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';
    try {
        const response = await fetch(`/api/pessoas?busca=${encodeURIComponent(busca)}`);
        const data = await response.json();
        if (data.success && data.pessoas) {
            if (data.pessoas.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhuma pessoa encontrada</div>';
            } else {
                lista.innerHTML = data.pessoas.map(p => {
                    const isMaster = user && user.tipo === 'master';
                    const isBloqueado = p.status === 'BLOQUEADO';
                    return `
                    <div class="pessoa-card ${isBloqueado ? 'card-bloqueado' : ''}">
                        <div class="pessoa-avatar">${getAvatarIcon(p.tipo)}</div>
                        <div class="pessoa-info">
                            <div class="pessoa-nome">${escapeHtml(p.nome)}</div>
                            <div class="pessoa-detalhes">
                                <span class="badge-tipo">${getTipoIcon(p.tipo)} ${p.tipo}</span>
                                <span class="badge-apartamento">🏠 ${p.apartamento || '-'}</span>
                                <span class="badge-telefone">📞 ${formatarTelefoneExibicao(p.telefone)}</span>
                                ${p.documento ? `<span class="badge-documento">🆔 ${formatarDocumentoExibicao(p.documento)}</span>` : ''}
                                ${isBloqueado ? '<span class="badge-bloqueado">🚫 BLOQUEADO</span>' : '<span class="badge-ativo">✅ ATIVO</span>'}
                            </div>
                            ${p.motivo_bloqueio ? `<div class="motivo-bloqueio">Motivo: ${escapeHtml(p.motivo_bloqueio)}</div>` : ''}
                        </div>

                      <div class="pessoa-actions">
    <button class="btn-entrada" style="width:36px; height:36px; display:inline-flex; align-items:center; justify-content:center; margin:0; padding:0;" onclick="abrirModalObservacao(${p.id}, '${escapeHtml(p.nome)}')" title="Registrar Entrada">🚪</button>
    <button class="btn-edit" style="width:36px; height:36px; display:inline-flex; align-items:center; justify-content:center; margin:0; padding:0;" onclick="editarPessoa(${p.id})" title="Editar">✏️</button>
    <button class="btn-bloquear" style="width:36px; height:36px; display:inline-flex; align-items:center; justify-content:center; margin:0; padding:0;" onclick="bloquearPessoa(${p.id}, '${escapeHtml(p.nome)}')" title="Bloquear">🔒</button>
    <button class="btn-delete" style="width:36px; height:36px; display:inline-flex; align-items:center; justify-content:center; margin:0; padding:0;" onclick="deletarPessoa(${p.id}, '${escapeHtml(p.nome)}')" title="Excluir">🗑️</button>
</div>
                        </div>
                    </div>`;
                }).join('');
            }
        }
    } catch (error) {
        lista.innerHTML = '<div class="loading">❌ Erro ao carregar</div>';
        console.error(error);
    }
}

function abrirModalPessoa() {
    document.getElementById('modalTitle').innerText = 'Nova Pessoa';
    document.getElementById('pessoaId').value = '';
    document.getElementById('pessoaNome').value = '';
    document.getElementById('pessoaTipo').value = 'morador';
    document.getElementById('pessoaApartamento').value = '';
    document.getElementById('pessoaTelefone').value = '';
    document.getElementById('pessoaDocumento').value = '';
    document.getElementById('pessoaVeiculo').value = '';

    const selectCondominio = document.getElementById('pessoaCondominio');
    if (user && user.tipo === 'master') {
        selectCondominio.style.display = 'block';
        carregarCondominiosParaSelectPessoa();
    } else {
        selectCondominio.style.display = 'none';
    }

    document.getElementById('modalPessoa').classList.add('active');
}

async function carregarCondominiosParaSelectPessoa() {
    try {
        const response = await fetch('/api/condominios');
        const data = await response.json();
        if (data.success && data.condominios) {
            const select = document.getElementById('pessoaCondominio');
            select.innerHTML = '<option value="">Selecione um condomínio</option>' +
                data.condominios.map(c => `<option value="${c.id}">${escapeHtml(c.nome)}</option>`).join('');
        }
    } catch (error) {}
}

function fecharModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    if (modalId === 'modalAviso') {
        document.getElementById('avisoId').value = '';
        document.getElementById('modalAvisoTitle').innerText = 'Novo Aviso';
    }
    if (modalId === 'modalOcorrencia') {
        document.getElementById('ocorrenciaId').value = '';
        document.getElementById('modalOcorrenciaTitle').innerText = 'Nova Ocorrência';
    }
    if (modalId === 'modalPessoa') {
        document.getElementById('pessoaId').value = '';
        document.getElementById('modalTitle').innerText = 'Nova Pessoa';
    }
}

async function salvarPessoa() {
    const id = document.getElementById('pessoaId').value;
    const nome = document.getElementById('pessoaNome').value.trim();
    if (!nome) { alert('Nome é obrigatório!'); return; }

    let telefone = document.getElementById('pessoaTelefone').value;
    let documento = document.getElementById('pessoaDocumento').value;
    telefone = limparFormatacao(telefone);
    documento = limparFormatacao(documento);

    if (documento.length === 11 && !validarCPF(documento)) {
        alert('❌ CPF inválido! Verifique o número digitado.');
        return;
    }

    const dados = {
        nome: nome,
        tipo: document.getElementById('pessoaTipo').value,
        apartamento: document.getElementById('pessoaApartamento').value,
        telefone: telefone,
        documento: documento,
        veiculo_placa: document.getElementById('pessoaVeiculo').value,
        veiculo_modelo: document.getElementById('pessoaVeiculo').value
    };

    if (user && user.tipo === 'master') {
        dados.condominio_id = document.getElementById('pessoaCondominio').value;
        if (!dados.condominio_id) {
            alert('Selecione um condomínio!');
            return;
        }
    }

    const url = id ? `/api/pessoas/${id}` : '/api/pessoas';
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        const data = await response.json();
        alert(data.message);
        if (data.success) {
            fecharModal('modalPessoa');
            await carregarPessoas();
            await carregarEstatisticas();
        }
    } catch (error) { alert('Erro ao salvar!'); }
}

async function editarPessoa(id) {
    try {
        const response = await fetch('/api/pessoas');
        const data = await response.json();
        const pessoa = data.pessoas.find(p => p.id === id);
        if (pessoa) {
            document.getElementById('modalTitle').innerText = 'Editar Pessoa';
            document.getElementById('pessoaId').value = pessoa.id;
            document.getElementById('pessoaNome').value = pessoa.nome;
            document.getElementById('pessoaTipo').value = pessoa.tipo;
            document.getElementById('pessoaApartamento').value = pessoa.apartamento || '';

            const telefoneInput = document.getElementById('pessoaTelefone');
            telefoneInput.value = pessoa.telefone || '';
            formatarTelefone(telefoneInput);

            const documentoInput = document.getElementById('pessoaDocumento');
            documentoInput.value = pessoa.documento || '';
            formatarDocumento(documentoInput);

            document.getElementById('pessoaVeiculo').value = pessoa.veiculo_placa || '';

            const selectCondominio = document.getElementById('pessoaCondominio');
            if (user && user.tipo === 'master') {
                selectCondominio.style.display = 'block';
                await carregarCondominiosParaSelectPessoa();
                selectCondominio.value = pessoa.condominio_id || '';
            } else {
                selectCondominio.style.display = 'none';
            }

            document.getElementById('modalPessoa').classList.add('active');
        }
    } catch (error) { alert('Erro ao carregar!'); }
}

async function deletarPessoa(id, nome) {
    if (!confirm(`Deletar ${nome}?`)) return;
    const response = await fetch(`/api/pessoas/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        await carregarPessoas();
        await carregarEstatisticas();
    }
}

async function registrarEntrada(id, nome) {
    try {
        const response = await fetch('/api/pessoas');
        const data = await response.json();
        const pessoa = data.pessoas.find(p => p.id === id);
        if (pessoa && pessoa.status === 'BLOQUEADO') {
            alert(`🚫 PESSOA BLOQUEADA!\n\n${nome} está BLOQUEADA(o).\nMotivo: ${pessoa.motivo_bloqueio || 'Não informado'}\n\nEntrada não permitida.`);
            return;
        }
    } catch (error) { console.error('Erro ao verificar bloqueio:', error); }

    if (!confirm(`Registrar entrada de ${nome}?`)) return;
    try {
        const response = await fetch('/api/registrar_entrada', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pessoa_id: id })
        });
        const data = await response.json();
        if (data.success) {
            const agora = new Date();
            const horaFormatada = agora.toLocaleTimeString('pt-BR');
            const dataFormatada = agora.toLocaleDateString('pt-BR');
            alert(`✅ ${data.message}\n\n📅 Data: ${dataFormatada}\n⏰ Hora: ${horaFormatada}`);
            await carregarRegistros();
            await carregarEstatisticas();
        } else { alert(`❌ ${data.error}`); }
    } catch (error) { alert('❌ Erro ao registrar entrada!'); }
}

async function bloquearPessoa(id, nome) {
    const motivo = prompt(`Motivo para bloquear ${nome}:`);
    if (!motivo) return;
    const response = await fetch(`/api/bloquear_pessoa/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ motivo })
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) await carregarPessoas();
}

async function desbloquearPessoa(id) {
    const response = await fetch(`/api/desbloquear_pessoa/${id}`, { method: 'POST' });
    const data = await response.json();
    alert(data.message);
    if (data.success) await carregarPessoas();
}

// ==================== REGISTROS ====================

async function carregarRegistros() {
    const lista = document.getElementById('listaRegistros');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando registros...</div>';
    try {
        const response = await fetch('/api/registros');
        const data = await response.json();
        if (data.success && data.registros) {
            if (data.registros.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhum registro encontrado</div>';
            } else {
                const isMaster = user && user.tipo === 'master';
                lista.innerHTML = data.registros.map(r => {
                    const dataHora = new Date(r.data_entrada);
                    const dataFormatada = dataHora.toLocaleDateString('pt-BR');
                    const horaFormatada = dataHora.toLocaleTimeString('pt-BR');
                    const diaSemana = obterDiaSemanaPT(r.data_entrada);
                    return `
                    <div class="registro-card">
                        <div class="registro-avatar">${getAvatarIcon(r.tipo)}</div>
                        <div class="registro-info">
                            <div class="registro-nome">${escapeHtml(r.nome)}</div>
                            <div class="registro-detalhes">
                                <span class="badge-tipo">${getTipoIcon(r.tipo)} ${r.tipo}</span>
                                <span class="badge-apartamento">🏠 ${r.apartamento || '-'}</span>
                            </div>
                            <div class="registro-data-hora">
                                <span class="registro-dia">📅 ${diaSemana}</span>
                                <span class="registro-data">${dataFormatada}</span>
                                <span class="registro-hora">⏰ ${horaFormatada}</span>
                            </div>
                            ${r.observacao ? `<div class="registro-observacao">📝 Observação: ${escapeHtml(r.observacao)}</div>` : ''}
                            <div class="registro-usuario">👤 Registrado por: ${r.usuario || 'Sistema'}</div>
                        </div>
                        ${isMaster ? `
                        <div class="registro-actions">
                            <button class="btn-delete" onclick="deletarRegistro(${r.id})" title="Excluir">🗑️</button>
                        </div>
                        ` : ''}
                    </div>`;
                }).join('');
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro ao carregar</div>'; }
}

async function deletarRegistro(id) {
    if (!confirm('Tem certeza que deseja deletar este registro?')) return;
    const response = await fetch(`/api/registros/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        await carregarRegistros();
        await carregarEstatisticas();
    }
}

// ==================== ESTATÍSTICAS ====================
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/estatisticas');
        const data = await response.json();
        if (data.success) {
            document.getElementById('totalPessoas').innerText = data.estatisticas.total_pessoas || 0;
            document.getElementById('totalRegistros').innerText = data.estatisticas.total_registros || 0;
            document.getElementById('registrosHoje').innerText = data.estatisticas.registros_hoje || 0;
            const hojeElement = document.querySelector('.stat-card:last-child .stat-label');
            if (hojeElement) {
                const dataHoje = new Date();
                const diaSemana = obterDiaSemanaPT(dataHoje);
                hojeElement.innerHTML = `Entradas ${diaSemana}`;
            }
        }
    } catch (error) { console.error('Erro estatisticas:', error); }
}

// ==================== AVISOS ====================
async function carregarAvisos() {
    const lista = document.getElementById('listaAvisos');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';
    try {
        const response = await fetch('/api/avisos');
        const data = await response.json();
        if (data.success && data.avisos) {
            if (data.avisos.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhum aviso</div>';
            } else {
                const isMaster = user && user.tipo === 'master';
                lista.innerHTML = data.avisos.map(a => {
                    const dataCriacao = new Date(a.data_criacao);
                    const dataFormatada = dataCriacao.toLocaleDateString('pt-BR');
                    const horaFormatada = dataCriacao.toLocaleTimeString('pt-BR');
                    return `
                    <div class="aviso-card aviso-${a.tipo}">
                        <div class="aviso-titulo">${a.tipo === 'urgente' ? '🔴' : a.tipo === 'alerta' ? '⚠️' : '📢'} ${escapeHtml(a.titulo)}</div>
                        <div class="aviso-mensagem">${escapeHtml(a.mensagem)}</div>
                        <div class="aviso-info">
                            <span>🏢 Condomínio: ${a.condominio_nome || 'Geral'}</span>
                            <span>👨‍💼 Criado por: ${a.criado_por_nome || 'Sistema'}</span>
                            <span>📅 ${dataFormatada} às ${horaFormatada}</span>
                        </div>
                        ${isMaster ? `
                        <div class="aviso-actions">
                            <button class="btn-edit" onclick="editarAviso(${a.id})">✏️ Editar</button>
                            <button class="btn-delete" onclick="deletarAviso(${a.id})">🗑️ Excluir</button>
                        </div>
                        ` : ''}
                    </div>`;
                }).join('');
            }
        }
    } catch (error) {
        lista.innerHTML = '<div class="loading">❌ Erro</div>';
        console.error(error);
    }
}

function abrirModalAviso() {
    document.getElementById('avisoId').value = '';
    document.getElementById('avisoTitulo').value = '';
    document.getElementById('avisoMensagem').value = '';
    document.getElementById('avisoTipo').value = 'info';
    document.getElementById('modalAvisoTitle').innerText = 'Novo Aviso';
    document.getElementById('modalAviso').classList.add('active');
}

function fecharModalAviso() {
    document.getElementById('modalAviso').classList.remove('active');
    document.getElementById('avisoId').value = '';
    document.getElementById('modalAvisoTitle').innerText = 'Novo Aviso';
}

async function salvarAviso() {
    const id = document.getElementById('avisoId').value;
    const titulo = document.getElementById('avisoTitulo').value.trim();
    const mensagem = document.getElementById('avisoMensagem').value.trim();
    if (!titulo || !mensagem) { alert('Preencha todos os campos!'); return; }

    const url = id ? `/api/avisos/${id}` : '/api/avisos';
    const method = id ? 'PUT' : 'POST';

    const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            titulo: titulo,
            tipo: document.getElementById('avisoTipo').value,
            mensagem: mensagem,
            ativo: 1
        })
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        fecharModalAviso();
        await carregarAvisos();
    }
}

async function editarAviso(id) {
    try {
        const response = await fetch('/api/avisos');
        const data = await response.json();
        const aviso = data.avisos.find(a => a.id === id);
        if (aviso) {
            document.getElementById('avisoId').value = aviso.id;
            document.getElementById('avisoTitulo').value = aviso.titulo;
            document.getElementById('avisoMensagem').value = aviso.mensagem;
            document.getElementById('avisoTipo').value = aviso.tipo;
            document.getElementById('modalAvisoTitle').innerText = 'Editar Aviso';
            document.getElementById('modalAviso').classList.add('active');
        }
    } catch (error) { alert('Erro ao carregar aviso!'); }
}

async function deletarAviso(id) {
    if (!confirm('Tem certeza que deseja deletar este aviso?')) return;
    const response = await fetch(`/api/avisos/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        await carregarAvisos();
    }
}

// ==================== FUNÇÕES DE AJUDA ====================
function abrirAjuda() {
    console.log("🔧 Abrindo ajuda...");

    // Verificar se já existe modal
    let modalExistente = document.getElementById('modalAjudaNovo');
    if (modalExistente) {
        modalExistente.remove();
    }

    // Criar modal
    const modalHTML = `
    <div id="modalAjudaNovo" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:99999;display:flex;justify-content:center;align-items:center;">
        <div style="background:white;border-radius:20px;width:90%;max-width:600px;max-height:85%;overflow-y:auto;box-shadow:0 10px 40px rgba(0,0,0,0.3);">
            <div style="background:linear-gradient(135deg,#FF9800,#F57C00);padding:20px;border-radius:20px 20px 0 0;display:flex;justify-content:space-between;align-items:center;">
                <h2 style="margin:0;color:white;font-size:22px;">📚 Guia Rápido - SmartCond</h2>
                <span onclick="fecharAjudaNovo()" style="font-size:32px;cursor:pointer;color:white;">&times;</span>
            </div>
            <div style="padding:20px;">
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">👥 Pessoas</h3>
                    <p><strong>🚪 Registrar Entrada</strong> - Registra a entrada da pessoa</p>
                    <p><strong>✏️ Editar</strong> - Altera os dados cadastrados</p>
                    <p><strong>🔒 Bloquear</strong> - Impede a entrada</p>
                    <p><strong>🗑️ Excluir</strong> - Remove a pessoa</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">📝 Registros</h3>
                    <p>Visualize todas as entradas com data, hora e quem registrou.</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">📢 Avisos</h3>
                    <p>Crie, edite e exclua avisos para os condôminos.</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">⚠️ Ocorrências</h3>
                    <p>Registre problemas com prioridade: Baixa, Média, Alta ou Urgente.</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">👮 Porteiros (Master)</h3>
                    <p>Gerencie os porteiros do sistema.</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">⚙️ Configurações</h3>
                    <p>Exportar relatórios Excel, gerenciar condomínios e backup.</p>
                </div>
                <div style="margin-bottom:15px;border-left:4px solid #FF9800;padding-left:15px;">
                    <h3 style="color:#F57C00;margin-bottom:5px;">🔑 Credenciais</h3>
                <p><strong>Porteiro:</strong> Credenciais fornecidas pelo administrador</p>
                </div>
                <div style="background:#FFF3E0;padding:10px;border-radius:10px;border-left:4px solid #FF9800;">
                    <strong>💡 Dica:</strong> Use a busca 🔍 para encontrar pessoas rapidamente!
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function fecharAjudaNovo() {
    const modal = document.getElementById('modalAjudaNovo');
    if (modal) {
        modal.remove();
    }
}

// ==================== OCORRÊNCIAS ====================
async function carregarOcorrencias() {
    console.log("🔄 Carregando ocorrências...");
    const lista = document.getElementById('listaOcorrencias');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';
    try {
        const response = await fetch('/api/ocorrencias');
        const data = await response.json();
        if (data.success && data.ocorrencias) {
            if (data.ocorrencias.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhuma ocorrência</div>';
            } else {
                const isMaster = user && user.tipo === 'master';
                lista.innerHTML = data.ocorrencias.map(o => {
                    const dataCriacao = new Date(o.data_criacao);
                    const dataFormatada = dataCriacao.toLocaleDateString('pt-BR');
                    const horaFormatada = dataCriacao.toLocaleTimeString('pt-BR');
                    return `
                    <div class="ocorrencia-card prioridade-${o.prioridade}">
                        <div class="ocorrencia-titulo">${o.prioridade === 'urgente' ? '🔴' : '📋'} ${escapeHtml(o.titulo)}</div>
                        <div class="ocorrencia-descricao">${escapeHtml(o.descricao)}</div>
                        <div class="ocorrencia-info">
                            <span>📋 ${o.tipo}</span>
                            <span>🎯 ${o.prioridade}</span>
                            <span>📌 ${o.status || 'aberto'}</span>
                            <span>👤 Responsável: ${o.responsavel || '-'}</span>
                            <span>🏢 Condomínio: ${o.condominio_nome || 'Não informado'}</span>
                            <span>👨‍💼 Criado por: ${o.criado_por_nome || 'Sistema'}</span>
                            <span>📅 ${dataFormatada} às ${horaFormatada}</span>
                        </div>
                        ${isMaster ? `
                        <div class="ocorrencia-actions">
                            <button class="btn-edit" onclick="editarOcorrencia(${o.id})">✏️ Editar</button>
                            <button class="btn-delete" onclick="deletarOcorrencia(${o.id})">🗑️ Excluir</button>
                        </div>
                        ` : ''}
                    </div>`;
                }).join('');
            }
        }
    } catch (error) {
        lista.innerHTML = '<div class="loading">❌ Erro</div>';
        console.error(error);
    }
}

function abrirModalOcorrencia() {
    document.getElementById('ocorrenciaId').value = '';
    document.getElementById('ocorrenciaTitulo').value = '';
    document.getElementById('ocorrenciaDescricao').value = '';
    document.getElementById('ocorrenciaTipo').value = 'reclamacao';
    document.getElementById('ocorrenciaPrioridade').value = 'media';
    document.getElementById('ocorrenciaStatus').value = 'aberto';
    document.getElementById('ocorrenciaResponsavel').value = '';
    document.getElementById('modalOcorrenciaTitle').innerText = 'Nova Ocorrência';
    document.getElementById('modalOcorrencia').classList.add('active');
}

function fecharModalOcorrencia() {
    document.getElementById('modalOcorrencia').classList.remove('active');
    document.getElementById('ocorrenciaId').value = '';
    document.getElementById('modalOcorrenciaTitle').innerText = 'Nova Ocorrência';
}

async function salvarOcorrencia() {
    console.log("🔧 salvarOcorrencia chamada");
    const id = document.getElementById('ocorrenciaId').value;
    const titulo = document.getElementById('ocorrenciaTitulo').value.trim();
    const descricao = document.getElementById('ocorrenciaDescricao').value.trim();
    const tipo = document.getElementById('ocorrenciaTipo').value;
    const prioridade = document.getElementById('ocorrenciaPrioridade').value;
    const status = document.getElementById('ocorrenciaStatus').value;
    const responsavel = document.getElementById('ocorrenciaResponsavel').value;

    if (!titulo) { alert('⚠️ O título é obrigatório!'); return; }
    if (!descricao) { alert('⚠️ A descrição é obrigatória!'); return; }

    const url = id ? `/api/ocorrencias/${id}` : '/api/ocorrencias';
    const method = id ? 'PUT' : 'POST';
    const dados = { titulo, descricao, tipo, prioridade, status, responsavel };

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        const data = await response.json();
        if (data.success) {
            alert('✅ Ocorrência salva com sucesso!');
            fecharModalOcorrencia();
            await carregarOcorrencias();
        } else {
            alert('❌ Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('❌ Erro ao salvar ocorrência:', error);
        alert('❌ Erro ao conectar ao servidor!');
    }
}

async function editarOcorrencia(id) {
    try {
        const response = await fetch('/api/ocorrencias');
        const data = await response.json();
        const ocorrencia = data.ocorrencias.find(o => o.id === id);
        if (ocorrencia) {
            document.getElementById('ocorrenciaId').value = ocorrencia.id;
            document.getElementById('ocorrenciaTitulo').value = ocorrencia.titulo;
            document.getElementById('ocorrenciaDescricao').value = ocorrencia.descricao;
            document.getElementById('ocorrenciaTipo').value = ocorrencia.tipo;
            document.getElementById('ocorrenciaPrioridade').value = ocorrencia.prioridade;
            document.getElementById('ocorrenciaStatus').value = ocorrencia.status || 'aberto';
            document.getElementById('ocorrenciaResponsavel').value = ocorrencia.responsavel || '';
            document.getElementById('modalOcorrenciaTitle').innerText = 'Editar Ocorrência';
            document.getElementById('modalOcorrencia').classList.add('active');
        }
    } catch (error) { alert('Erro ao carregar ocorrência!'); }
}

async function deletarOcorrencia(id) {
    if (!confirm('Tem certeza que deseja deletar esta ocorrência?')) return;
    const response = await fetch(`/api/ocorrencias/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        await carregarOcorrencias();
    }
}

// ==================== PORTEIROS ====================
async function carregarPorteiros() {
    console.log("🔄 Carregando porteiros...");
    const lista = document.getElementById('listaPorteiros');
    if (!lista) {
        console.error("Elemento 'listaPorteiros' não encontrado");
        return;
    }

    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';

    try {
        const response = await fetch('/api/porteiros');
        const data = await response.json();
        console.log("Resposta porteiros:", data);

        if (data.success && data.porteiros) {
            if (data.porteiros.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhum porteiro cadastrado</div>';
            } else {
                lista.innerHTML = data.porteiros.map(p => `
                    <div class="porteiro-card">
                        <div class="porteiro-avatar">👮</div>
                        <div class="porteiro-info">
                            <div class="porteiro-nome">${escapeHtml(p.nome)}</div>
                            <div class="porteiro-detalhes">
                                <span>👤 Login: ${escapeHtml(p.login)}</span>
                                <span>🏢 Condomínio: ${escapeHtml(p.condominio_nome) || 'Não definido'}</span>
                                <span>${p.ativo ? '✅ Ativo' : '❌ Inativo'}</span>
                            </div>
                        </div>
                        <div class="porteiro-actions">
                            <button class="btn-edit" onclick="editarPorteiro(${p.id})" title="Editar">✏️</button>
                            <button class="btn-delete" onclick="deletarPorteiro(${p.id}, '${escapeHtml(p.nome)}')" title="Excluir">🗑️</button>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            lista.innerHTML = '<div class="loading">❌ Erro: ' + (data.error || 'Falha ao carregar') + '</div>';
        }
    } catch (error) {
        console.error('❌ Erro ao carregar porteiros:', error);
        lista.innerHTML = '<div class="loading">❌ Erro ao conectar ao servidor</div>';
    }
}

function abrirModalPorteiro() {
    document.getElementById('porteiroId').value = '';
    document.getElementById('porteiroNome').value = '';
    document.getElementById('porteiroLogin').value = '';
    document.getElementById('porteiroSenha').value = '';
    document.getElementById('porteiroSenha').placeholder = 'Senha';
    document.getElementById('porteiroAtivo').checked = true;
    document.getElementById('modalPorteiroTitle').innerText = 'Novo Porteiro';
    carregarCondominiosParaSelect();
    document.getElementById('modalPorteiro').classList.add('active');
}

function fecharModalPorteiro() {
    document.getElementById('modalPorteiro').classList.remove('active');
    document.getElementById('porteiroId').value = '';
}

async function editarPorteiro(id) {
    try {
        const response = await fetch('/api/porteiros');
        const data = await response.json();
        const porteiro = data.porteiros.find(p => p.id === id);
        if (porteiro) {
            await carregarCondominiosParaSelect();
            document.getElementById('porteiroId').value = porteiro.id;
            document.getElementById('porteiroNome').value = porteiro.nome;
            document.getElementById('porteiroLogin').value = porteiro.login;
            document.getElementById('porteiroSenha').value = '';
            document.getElementById('porteiroSenha').placeholder = 'Deixe em branco para manter';
            document.getElementById('porteiroAtivo').checked = porteiro.ativo === 1;
            const select = document.getElementById('porteiroCondominio');
            if (select && porteiro.condominio_id) select.value = porteiro.condominio_id;
            document.getElementById('modalPorteiroTitle').innerText = 'Editar Porteiro';
            document.getElementById('modalPorteiro').classList.add('active');
        }
    } catch (error) { alert('Erro ao carregar!'); }
}

async function carregarCondominiosParaSelect() {
    try {
        const response = await fetch('/api/condominios');
        const data = await response.json();
        if (data.success && data.condominios) {
            const select = document.getElementById('porteiroCondominio');
            if (select) {
                select.innerHTML = '<option value="">Selecione um condomínio</option>' +
                    data.condominios.map(c => `<option value="${c.id}">${escapeHtml(c.nome)}</option>`).join('');
            }
        }
    } catch (error) { console.error('Erro ao carregar condomínios:', error); }
}

async function salvarPorteiro() {
    console.log("🔧 Salvar porteiro chamado");

    const id = document.getElementById('porteiroId')?.value;
    const nome = document.getElementById('porteiroNome').value.trim();
    const login = document.getElementById('porteiroLogin').value.trim();
    const senha = document.getElementById('porteiroSenha').value;
    const condominio_id = document.getElementById('porteiroCondominio').value;
    const ativo = document.getElementById('porteiroAtivo')?.checked || true;

    console.log("Dados:", { id, nome, login, condominio_id, ativo, senha: senha ? '***' : '(vazio)' });

    if (!nome || !login) {
        alert('⚠️ Nome e login são obrigatórios!');
        return;
    }

    if (!condominio_id) {
        alert('⚠️ Selecione um condomínio!');
        return;
    }

    if (!senha && !id) {
        alert('⚠️ Senha é obrigatória para novo porteiro!');
        return;
    }

    const url = id ? `/api/porteiros/${id}` : '/api/porteiros';
    const method = id ? 'PUT' : 'POST';
    const dados = { nome, login, condominio_id, ativo };
    if (senha) dados.senha = senha;

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        const data = await response.json();
        console.log("Resposta:", data);

        if (data.success) {
            alert('✅ ' + data.message);
            fecharModalPorteiro();
            await carregarPorteiros();
        } else {
            alert('❌ Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('❌ Erro ao salvar porteiro:', error);
        alert('❌ Erro ao conectar ao servidor!');
    }
}

async function deletarPorteiro(id, nome) {
    if (!confirm(`Deletar porteiro ${nome}?`)) return;
    const response = await fetch(`/api/porteiros/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) await carregarPorteiros();
}

// ==================== CONDOMÍNIOS ====================
async function carregarCondominios() {
    const lista = document.getElementById('listaCondominios');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';
    try {
        const response = await fetch('/api/condominios');
        const data = await response.json();
        if (data.success && data.condominios) {
            if (data.condominios.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhum condomínio</div>';
            } else {
                lista.innerHTML = data.condominios.map(c => `
                    <div class="condominio-item">
                        <div class="condominio-avatar">🏢</div>
                        <div class="condominio-info">
                            <div class="condominio-nome">${escapeHtml(c.nome)}</div>
                            <div class="condominio-detalhes">
                                <span>📍 ${c.endereco || '-'}</span>
                                <span>📞 ${c.telefone || '-'}</span>
                            </div>
                        </div>
                        <button class="btn-delete" onclick="deletarCondominio(${c.id}, '${escapeHtml(c.nome)}')">🗑️</button>
                    </div>
                `).join('');
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro</div>'; }
}

async function deletarCondominio(id, nome) {
    if (!confirm(`Deletar condomínio ${nome}?`)) return;
    const response = await fetch(`/api/condominios/${id}`, { method: 'DELETE' });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        await carregarCondominios();
        await carregarCondominiosParaSelect();
    }
}

function abrirModalCondominio() {
    document.getElementById('condominioNome').value = '';
    document.getElementById('condominioEndereco').value = '';
    document.getElementById('condominioTelefone').value = '';
    document.getElementById('modalCondominio').classList.add('active');
}

function fecharModalCondominio() { document.getElementById('modalCondominio').classList.remove('active'); }

async function salvarCondominio() {
    const nome = document.getElementById('condominioNome').value.trim();
    if (!nome) { alert('Nome é obrigatório!'); return; }
    const response = await fetch('/api/condominios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nome: nome,
            endereco: document.getElementById('condominioEndereco').value,
            telefone: document.getElementById('condominioTelefone').value
        })
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        fecharModalCondominio();
        await carregarCondominios();
        await carregarCondominiosParaSelect();
    }
}

// ==================== RELATÓRIOS EXCEL ====================
async function exportarRelatorioRegistros() {
    try {
        const btn = event.target;
        const textoOriginal = btn.innerText;
        btn.innerText = '⏳ Gerando relatório...';
        btn.disabled = true;
        const response = await fetch('/api/relatorio_registros');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'relatorio_registros.xlsx';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match && match[1]) filename = match[1].replace(/['"]/g, '');
            }
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            alert('✅ Relatório gerado com sucesso!');
        } else {
            const error = await response.json();
            alert('❌ Erro ao gerar relatório: ' + (error.error || 'Erro desconhecido'));
        }
        btn.innerText = textoOriginal;
        btn.disabled = false;
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao gerar relatório!');
        event.target.innerText = '📑 Exportar Registros (Excel)';
        event.target.disabled = false;
    }
}

async function exportarRelatorioPessoas() {
    try {
        const btn = event.target;
        const textoOriginal = btn.innerText;
        btn.innerText = '⏳ Gerando relatório...';
        btn.disabled = true;
        const response = await fetch('/api/relatorio_pessoas');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'relatorio_pessoas.xlsx';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match && match[1]) filename = match[1].replace(/['"]/g, '');
            }
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            alert('✅ Relatório gerado com sucesso!');
        } else {
            const error = await response.json();
            alert('❌ Erro ao gerar relatório: ' + (error.error || 'Erro desconhecido'));
        }
        btn.innerText = textoOriginal;
        btn.disabled = false;
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao gerar relatório!');
        event.target.innerText = '👥 Exportar Pessoas (Excel)';
        event.target.disabled = false;
    }
}

// ==================== BACKUP E ZERAR BANCO ====================
async function criarBackup() {
    const response = await fetch('/api/backup', { method: 'POST' });
    const data = await response.json();
    alert(data.message);
}

async function zerarBanco() {
    console.log("🔧 Função zerarBanco chamada");
    if (!confirm('⚠️ ATENÇÃO! Isso vai apagar TODAS as pessoas, registros, avisos e ocorrências.\n\nAs senhas, porteiros e condomínios serão mantidos.\n\nTem certeza?')) {
        console.log("❌ Cancelado pelo usuário");
        return;
    }
    const confirmacao = prompt('Digite "ZERAR" para confirmar a exclusão:');
    console.log("Confirmacao digitada:", confirmacao);
    if (confirmacao !== 'ZERAR') {
        alert('❌ Operação cancelada!');
        return;
    }
    try {
        console.log("🚀 Enviando requisição para /api/zerar_banco");
        const response = await fetch('/api/zerar_banco', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        console.log("📥 Resposta:", data);
        if (data.success) {
            alert('✅ ' + data.message);
            await carregarPessoas();
            await carregarRegistros();
            await carregarEstatisticas();
            await carregarAvisos();
            await carregarOcorrencias();
            console.log("✅ Todas as listas recarregadas");
        } else {
            alert('❌ Erro: ' + (data.error || 'Falha ao zerar banco'));
        }
    } catch (error) {
        console.error('❌ Erro ao zerar banco:', error);
        alert('❌ Erro ao conectar ao servidor!');
    }
}

// ==================== TABS ====================
function mostrarTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.querySelector(`.tab-btn[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`tab${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');
    if (tab === 'pessoas') carregarPessoas();
    if (tab === 'registros') carregarRegistros();
    if (tab === 'dashboard') carregarEstatisticas();
    if (tab === 'avisos') carregarAvisos();
    if (tab === 'ocorrencias') carregarOcorrencias();
    if (tab === 'porteiros') carregarPorteiros();
    if (tab === 'config') carregarCondominios();
}

// ==================== INICIALIZAÇÃO ====================
document.getElementById('searchPessoa')?.addEventListener('keyup', () => carregarPessoas());
document.getElementById('senha')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') fazerLogin(); });

window.zerarBanco = zerarBanco;

// ==================== REGISTRO COM OBSERVAÇÃO ====================
function abrirModalObservacao(pessoaId, pessoaNome) {
    // Verificar bloqueio primeiro
    verificarBloqueioAntesDeRegistrar(pessoaId, pessoaNome);
}

async function verificarBloqueioAntesDeRegistrar(pessoaId, pessoaNome) {
    try {
        const response = await fetch('/api/pessoas');
        const data = await response.json();
        const pessoa = data.pessoas.find(p => p.id === pessoaId);

        if (pessoa && pessoa.status === 'BLOQUEADO') {
            alert(`🚫 ENTRADA BLOQUEADA!\n\n${pessoaNome} está BLOQUEADA(o).\nMotivo: ${pessoa.motivo_bloqueio || 'Não informado'}\n\nEntrada não permitida.`);
            return;
        }

        // Se não estiver bloqueado, abrir modal para observação
        const observacao = prompt(`📝 Registrar entrada de ${pessoaNome}\n\nDigite uma observação (opcional):`, '');

        if (observacao !== null) { // Não cancelou
            await registrarEntradaComObservacao(pessoaId, pessoaNome, observacao);
        }
    } catch (error) {
        console.error('Erro ao verificar bloqueio:', error);
        alert('Erro ao verificar bloqueio!');
    }
}

async function registrarEntradaComObservacao(pessoaId, pessoaNome, observacao) {
    try {
        const response = await fetch('/api/registrar_entrada', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pessoa_id: pessoaId,
                observacao: observacao
            })
        });
        const data = await response.json();
        if (data.success) {
            const agora = new Date();
            const horaFormatada = agora.toLocaleTimeString('pt-BR');
            const dataFormatada = agora.toLocaleDateString('pt-BR');
            let msg = `✅ ${data.message}\n\n📅 Data: ${dataFormatada}\n⏰ Hora: ${horaFormatada}`;
            if (observacao) msg += `\n📝 Observação: ${observacao}`;
            alert(msg);
            await carregarRegistros();
            await carregarEstatisticas();
        } else {
            alert(`❌ ${data.error}`);
        }
    } catch (error) {
        console.error('Erro ao registrar entrada:', error);
        alert('❌ Erro ao registrar entrada!');
    }
}

// ==================== BLOQUEIO COM MODAL ====================
function abrirModalBloqueio(id, nome) {
    console.log("🔧 Abrindo modal de bloqueio para:", nome);
    document.getElementById('bloqueioId').value = id;
    document.getElementById('bloqueioNome').value = nome;
    document.getElementById('bloqueioTexto').innerHTML = `Deseja bloquear <strong>${escapeHtml(nome)}</strong>?<br><br>Digite o motivo do bloqueio:`;
    document.getElementById('bloqueioMotivo').value = '';
    document.getElementById('modalBloqueio').classList.add('active');
}

function fecharModalBloqueio() {
    document.getElementById('modalBloqueio').classList.remove('active');
    document.getElementById('bloqueioId').value = '';
    document.getElementById('bloqueioNome').value = '';
    document.getElementById('bloqueioMotivo').value = '';
}

async function confirmarBloqueio() {
    const id = document.getElementById('bloqueioId').value;
    const nome = document.getElementById('bloqueioNome').value;
    const motivo = document.getElementById('bloqueioMotivo').value.trim();

    if (!motivo) {
        alert('⚠️ Digite o motivo do bloqueio!');
        return;
    }

    try {
        const response = await fetch(`/api/bloquear_pessoa/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo: motivo })
        });
        const data = await response.json();

        if (data.success) {
            alert(`✅ ${nome} foi BLOQUEADO com sucesso!\n\nMotivo: ${motivo}`);
            fecharModalBloqueio();
            await carregarPessoas();
            await carregarEstatisticas();
        } else {
            alert(`❌ Erro ao bloquear: ${data.error}`);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao conectar ao servidor!');
    }
}

// Substituir a função bloquearPessoa original
window.bloquearPessoa = function(id, nome) {
    console.log("🔧 bloquearPessoa chamada para:", nome);
    abrirModalBloqueio(id, nome);
};


console.log('✅ App carregado com sucesso!');
