// ==================== VARIÁVEIS GLOBAIS ====================
let user = null;

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
                lista.innerHTML = `<div class="cards-horizontal">` + data.pessoas.map(p => {
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
                                <span class="badge-telefone">📞 ${p.telefone || '-'}</span>
                                ${isBloqueado ? '<span class="badge-bloqueado">🚫 BLOQUEADO</span>' : '<span class="badge-ativo">✅ ATIVO</span>'}
                            </div>
                            ${p.motivo_bloqueio ? `<div class="motivo-bloqueio">Motivo: ${escapeHtml(p.motivo_bloqueio)}</div>` : ''}
                        </div>
                        <div class="pessoa-actions">
                            <button class="btn-entrada" onclick="registrarEntrada(${p.id}, '${escapeHtml(p.nome)}')" title="Registrar Entrada">🚪</button>
                            <button class="btn-edit" onclick="editarPessoa(${p.id})" title="Editar">✏️</button>
                            ${isMaster ? `
                                ${isBloqueado ?
                                    `<button class="btn-desbloquear" onclick="desbloquearPessoa(${p.id})" title="Desbloquear">🔓</button>` :
                                    `<button class="btn-bloquear" onclick="bloquearPessoa(${p.id}, '${escapeHtml(p.nome)}')" title="Bloquear">🔒</button>`
                                }
                                <button class="btn-delete" onclick="deletarPessoa(${p.id}, '${escapeHtml(p.nome)}')" title="Excluir">🗑️</button>
                            ` : ''}
                        </div>
                    </div>`;
                }).join('') + `</div>`;
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro ao carregar</div>'; }
}

function getAvatarIcon(tipo) {
    const icons = { 'morador': '👨‍👩‍👧', 'visitante': '👥', 'entregador': '📦', 'tecnico': '🔧' };
    return icons[tipo] || '👤';
}

function getTipoIcon(tipo) {
    const icons = { 'morador': '🏠', 'visitante': '👥', 'entregador': '📦', 'tecnico': '🔧' };
    return icons[tipo] || '📌';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
    document.getElementById('modalPessoa').classList.add('active');
}

function fecharModal() { document.getElementById('modalPessoa').classList.remove('active'); }

async function salvarPessoa() {
    const id = document.getElementById('pessoaId').value;
    const nome = document.getElementById('pessoaNome').value.trim();
    if (!nome) { alert('Nome é obrigatório!'); return; }
    const url = id ? `/api/pessoas/${id}` : '/api/pessoas';
    const method = id ? 'PUT' : 'POST';
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome: nome,
                tipo: document.getElementById('pessoaTipo').value,
                apartamento: document.getElementById('pessoaApartamento').value,
                telefone: document.getElementById('pessoaTelefone').value,
                documento: document.getElementById('pessoaDocumento').value,
                veiculo_placa: document.getElementById('pessoaVeiculo').value,
                veiculo_modelo: document.getElementById('pessoaVeiculo').value
            })
        });
        const data = await response.json();
        alert(data.message);
        if (data.success) {
            fecharModal();
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
            document.getElementById('pessoaTelefone').value = pessoa.telefone || '';
            document.getElementById('pessoaDocumento').value = pessoa.documento || '';
            document.getElementById('pessoaVeiculo').value = pessoa.veiculo_placa || '';
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
    // Verificar se a pessoa está bloqueada antes de tentar
    try {
        const response = await fetch('/api/pessoas');
        const data = await response.json();
        const pessoa = data.pessoas.find(p => p.id === id);

        if (pessoa && pessoa.status === 'BLOQUEADO') {
            alert(`🚫 PESSOA BLOQUEADA!\n\n${nome} está BLOQUEADA(o).\nMotivo: ${pessoa.motivo_bloqueio || 'Não informado'}\n\nEntrada não permitida.`);
            return;
        }
    } catch (error) {
        console.error('Erro ao verificar bloqueio:', error);
    }

    if (!confirm(`Registrar entrada de ${nome}?`)) return;

    try {
        const response = await fetch('/api/registrar_entrada', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pessoa_id: id })
        });
        const data = await response.json();

        if (data.success) {
            // Exibir hora da entrada
            const agora = new Date();
            const horaFormatada = agora.toLocaleTimeString('pt-BR');
            const dataFormatada = agora.toLocaleDateString('pt-BR');
            alert(`✅ ${data.message}\n\n📅 Data: ${dataFormatada}\n⏰ Hora: ${horaFormatada}`);

            await carregarRegistros();
            await carregarEstatisticas();
        } else {
            alert(`❌ ${data.error}`);
        }
    } catch (error) {
        alert('❌ Erro ao registrar entrada!');
    }
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
                lista.innerHTML = `<div class="cards-horizontal-registros">` + data.registros.map(r => {
                    const dataHora = new Date(r.data_entrada);
                    const dataFormatada = dataHora.toLocaleDateString('pt-BR');
                    const horaFormatada = dataHora.toLocaleTimeString('pt-BR');
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
                                <span class="registro-data">📅 ${dataFormatada}</span>
                                <span class="registro-hora">⏰ ${horaFormatada}</span>
                            </div>
                            <div class="registro-usuario">👤 Registrado por: ${r.usuario || 'Sistema'}</div>
                        </div>
                    </div>`;
                }).join('') + `</div>`;
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro ao carregar</div>'; }
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
                lista.innerHTML = `<div class="cards-horizontal-avisos">` + data.avisos.map(a => `
                    <div class="aviso-card aviso-${a.tipo}">
                        <div class="aviso-titulo">${a.tipo === 'urgente' ? '🔴' : a.tipo === 'alerta' ? '⚠️' : '📢'} ${escapeHtml(a.titulo)}</div>
                        <div class="aviso-mensagem">${escapeHtml(a.mensagem)}</div>
                        <div class="aviso-data">📅 ${a.data_criacao}</div>
                    </div>
                `).join('') + `</div>`;
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro</div>'; }
}

function abrirModalAviso() {
    document.getElementById('avisoTitulo').value = '';
    document.getElementById('avisoTipo').value = 'info';
    document.getElementById('avisoMensagem').value = '';
    document.getElementById('modalAviso').classList.add('active');
}

function fecharModalAviso() { document.getElementById('modalAviso').classList.remove('active'); }

async function salvarAviso() {
    const titulo = document.getElementById('avisoTitulo').value.trim();
    const mensagem = document.getElementById('avisoMensagem').value.trim();
    if (!titulo || !mensagem) { alert('Preencha todos os campos!'); return; }
    const response = await fetch('/api/avisos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            titulo: titulo,
            tipo: document.getElementById('avisoTipo').value,
            mensagem: mensagem
        })
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        fecharModalAviso();
        await carregarAvisos();
    }
}

// ==================== OCORRÊNCIAS ====================
async function carregarOcorrencias() {
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
                lista.innerHTML = `<div class="cards-horizontal-ocorrencias">` + data.ocorrencias.map(o => `
                    <div class="ocorrencia-card prioridade-${o.prioridade}">
                        <div class="ocorrencia-titulo">${o.prioridade === 'urgente' ? '🔴' : '📋'} ${escapeHtml(o.titulo)}</div>
                        <div class="ocorrencia-descricao">${escapeHtml(o.descricao)}</div>
                        <div class="ocorrencia-info">
                            <span>📋 ${o.tipo}</span>
                            <span>👤 ${o.responsavel || '-'}</span>
                            <span>📅 ${o.data_criacao}</span>
                        </div>
                    </div>
                `).join('') + `</div>`;
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro</div>'; }
}

function abrirModalOcorrencia() {
    document.getElementById('ocorrenciaTitulo').value = '';
    document.getElementById('ocorrenciaTipo').value = 'reclamacao';
    document.getElementById('ocorrenciaPrioridade').value = 'media';
    document.getElementById('ocorrenciaDescricao').value = '';
    document.getElementById('ocorrenciaResponsavel').value = '';
    document.getElementById('modalOcorrencia').classList.add('active');
}

function fecharModalOcorrencia() { document.getElementById('modalOcorrencia').classList.remove('active'); }

async function salvarOcorrencia() {
    const titulo = document.getElementById('ocorrenciaTitulo').value.trim();
    const descricao = document.getElementById('ocorrenciaDescricao').value.trim();
    if (!titulo || !descricao) { alert('Preencha os campos!'); return; }
    const response = await fetch('/api/ocorrencias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            titulo: titulo,
            tipo: document.getElementById('ocorrenciaTipo').value,
            prioridade: document.getElementById('ocorrenciaPrioridade').value,
            descricao: descricao,
            responsavel: document.getElementById('ocorrenciaResponsavel').value
        })
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) {
        fecharModalOcorrencia();
        await carregarOcorrencias();
    }
}

// ==================== PORTEIROS ====================
async function carregarPorteiros() {
    const lista = document.getElementById('listaPorteiros');
    if (!lista) return;
    lista.innerHTML = '<div class="loading">🔄 Carregando...</div>';
    try {
        const response = await fetch('/api/porteiros');
        const data = await response.json();
        if (data.success && data.porteiros) {
            if (data.porteiros.length === 0) {
                lista.innerHTML = '<div class="loading">📭 Nenhum porteiro</div>';
            } else {
                lista.innerHTML = `<div class="cards-horizontal">` + data.porteiros.map(p => `
                    <div class="porteiro-card">
                        <div class="porteiro-avatar">👮</div>
                        <div class="porteiro-info">
                            <div class="porteiro-nome">${escapeHtml(p.nome)}</div>
                            <div class="porteiro-detalhes">
                                <span>👤 ${p.login}</span>
                                <span>🏢 ${p.condominio_nome || 'Todos'}</span>
                            </div>
                        </div>
                        <div class="porteiro-actions">
                            <button class="btn-edit" onclick="editarPorteiro(${p.id})">✏️</button>
                            <button class="btn-delete" onclick="deletarPorteiro(${p.id}, '${escapeHtml(p.nome)}')">🗑️</button>
                        </div>
                    </div>
                `).join('') + `</div>`;
            }
        }
    } catch (error) { lista.innerHTML = '<div class="loading">❌ Erro</div>'; }
}

function abrirModalPorteiro() {
    carregarCondominiosParaSelect();
    document.getElementById('porteiroId').value = '';
    document.getElementById('porteiroNome').value = '';
    document.getElementById('porteiroLogin').value = '';
    document.getElementById('porteiroSenha').value = '';
    document.getElementById('porteiroAtivo').checked = true;
    document.getElementById('modalPorteiroTitle').innerText = 'Novo Porteiro';
    document.getElementById('modalPorteiro').classList.add('active');
}

function fecharModalPorteiro() { document.getElementById('modalPorteiro').classList.remove('active'); }

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
            select.innerHTML = '<option value="">Selecione um condomínio</option>' +
                data.condominios.map(c => `<option value="${c.id}">${escapeHtml(c.nome)}</option>`).join('');
        }
    } catch (error) {}
}

async function salvarPorteiro() {
    const id = document.getElementById('porteiroId')?.value;
    const nome = document.getElementById('porteiroNome').value.trim();
    const login = document.getElementById('porteiroLogin').value.trim();
    const senha = document.getElementById('porteiroSenha').value;
    const condominio_id = document.getElementById('porteiroCondominio').value;
    const ativo = document.getElementById('porteiroAtivo').checked;

    if (!nome || !login) { alert('Nome e login são obrigatórios!'); return; }
    if (!condominio_id) { alert('Selecione um condomínio!'); return; }
    if (!senha && !id) { alert('Senha é obrigatória!'); return; }

    const url = id ? `/api/porteiros/${id}` : '/api/porteiros';
    const method = id ? 'PUT' : 'POST';
    const dados = { nome, login, condominio_id, ativo };
    if (senha) dados.senha = senha;

    try {
        const response = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
        const data = await response.json();
        alert(data.message);
        if (data.success) {
            fecharModalPorteiro();
            await carregarPorteiros();
        }
    } catch (error) { alert('Erro ao salvar!'); }
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
                lista.innerHTML = `<div class="cards-horizontal">` + data.condominios.map(c => `
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
                `).join('') + `</div>`;
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

// ==================== ZERAR BANCO ====================
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

// ==================== BACKUP ====================
async function criarBackup() {
    const response = await fetch('/api/backup', { method: 'POST' });
    const data = await response.json();
    alert(data.message);
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

console.log('✅ App carregado com sucesso!');