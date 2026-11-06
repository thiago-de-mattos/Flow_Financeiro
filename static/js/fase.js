const formulario = document.getElementById("form-resposta");

if (formulario) {
    const campos = document.getElementById("campos-resposta");
    const confirmar = document.getElementById("btn-confirmar");
    const continuar = document.getElementById("btn-continuar");

    const feedback = document.getElementById("feedback-resposta");
    const titulo = document.getElementById("titulo-feedback");
    const explicacao = document.getElementById("explicacao-feedback");
    const resumo = document.getElementById("resumo-feedback");

    function lerResposta() {
        const tipo = formulario.dataset.tipo;

        if (tipo === "match") {
            const pares = {};

            formulario.querySelectorAll("select[data-termo]").forEach((select) => {
                pares[select.dataset.termo] = select.value;
            });

            return pares;
        }

        const valor = new FormData(formulario).get("resposta");

        if (tipo === "tf") {
            return valor === "true";
        }

        if (tipo === "mc") {
            return Number(valor);
        }

        return valor.trim();
    }

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        if (confirmar.disabled) return;

        // Lê antes de desabilitar. O FormData ignora campos desabilitados.
        const resposta = lerResposta();

        if (resposta === "") {
            document.getElementById("palavra").focus();
            return;
        }

        confirmar.disabled = true;
        confirmar.textContent = "Conferindo...";
        campos.disabled = true;

        try {
            const retorno = await fetch(formulario.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": formulario.elements.csrfmiddlewaretoken.value,
                },
                body: JSON.stringify({
                    question_id: Number(formulario.dataset.pergunta),
                    answer: resposta,
                }),
            });

            if (!retorno.ok || retorno.redirected) {
                throw new Error("Falha ao confirmar a resposta.");
            }

            const resultado = await retorno.json();

            const painelVidas = document.getElementById("vidas-fase");

            if (painelVidas) {
                const coracoes = painelVidas.querySelectorAll(".fase-coracao");
                const vidasVisiveis = resultado.game_over ? 0 : resultado.vidas;

                coracoes.forEach((coracao, indice) => {
                    const temVida = indice < vidasVisiveis;

                    coracao.textContent = temVida ? "♥" : "♡";
                    coracao.classList.toggle("sem-vida", !temVida);
                });

                painelVidas.setAttribute(
                    "aria-label",
                    `${vidasVisiveis} de ${coracoes.length} vidas restantes`
                );
            }

            const saldoMoedas = document.getElementById("saldo-moedas");
            saldoMoedas.textContent = resultado.profile.coins;

            const notificacoes = document.getElementById("notificacoes-conquistas");

            for (const conquista of resultado.badges) {
                const aviso = document.createElement("div");
                aviso.className = "aviso-conquista";

                const rotulo = document.createElement("small");
                rotulo.textContent = "🏆 Conquista desbloqueada";

                const nome = document.createElement("strong");
                nome.textContent = conquista.title;

                aviso.append(rotulo, nome);
                notificacoes.appendChild(aviso);

                window.setTimeout(() => aviso.remove(), 5000);
            }

            explicacao.textContent = resultado.explicacao;

            if (resultado.game_over) {
                titulo.textContent = "As vidas acabaram";
                resumo.textContent = "A próxima tentativa começa na primeira pergunta.";
                continuar.textContent = "Recomeçar fase";

            } else if (resultado.acertou) {
                titulo.textContent = resultado.fase_concluida
                    ? "Fase concluída!"
                    : "Resposta correta!";

                const detalhes = [];
                const premio = resultado.recompensa;

                if (premio.xp || premio.moedas) {
                    detalhes.push(`+${premio.xp} XP e +${premio.moedas} moedas`);
                }

                for (const conquista of resultado.badges) {
                    detalhes.push(`Conquista desbloqueada: ${conquista.title}`);
                }

                resumo.textContent = detalhes.join(" · ");

                if (resultado.fase_concluida) {
                    continuar.textContent = "Voltar à trilha";
                    continuar.href = continuar.dataset.trilha;
                } else {
                    continuar.textContent = "Próxima pergunta";
                }

            } else {
                titulo.textContent = "Resposta incorreta";
                resumo.textContent = `Vidas restantes: ${resultado.vidas}`;
                continuar.textContent = "Tentar novamente";
            }
        } catch {
            titulo.textContent = "Não foi possível confirmar o resultado";
            explicacao.textContent = "Reabra a fase para carregar o progresso salvo.";
            resumo.textContent = "";
            continuar.textContent = "Reabrir fase";
        }

        confirmar.hidden = true;
        feedback.hidden = false;
        continuar.hidden = false;
        continuar.focus();
    });
}