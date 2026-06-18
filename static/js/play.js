(() => {
  const root = document.querySelector(".ff-play-wrap");
  if (!root) return;

  const questions = JSON.parse(document.getElementById("ff-question-data").textContent);
  const serverCompleted = JSON.parse(document.getElementById("ff-completed-data").textContent);
  const storageKey = root.dataset.storageKey;
  const completeUrl = root.dataset.completeUrl;
  const csrfToken = document.querySelector(".ff-play-csrf [name=csrfmiddlewaretoken]")?.value || "";

  const modal = document.getElementById("ffQuizModal");
  const closeButton = document.getElementById("ffQuizClose");
  const continueButton = document.getElementById("ffContinue");
  const title = document.getElementById("ffQuizTitle");
  const statement = document.getElementById("ffQuizStatement");
  const level = document.getElementById("ffQuizLevel");
  const feedback = document.getElementById("ffFeedback");
  const feedbackTitle = document.getElementById("ffFeedbackTitle");
  const feedbackText = document.getElementById("ffFeedbackText");
  const rewardText = document.getElementById("ffRewardText");
  const completedCount = document.getElementById("ffCompletedCount");
  const progressFill = document.getElementById("ffProgressFill");
  const coins = document.getElementById("ffPlayCoins");
  const hearts = Array.from(document.querySelectorAll("#ffHearts span"));
  const answerButtons = Array.from(document.querySelectorAll(".ff-answer"));
  const steps = Array.from(document.querySelectorAll(".ff-path-step"));

  let completed = new Set([...serverCompleted, ...readLocalProgress()].map(Number));
  let activeQuestion = null;
  let heartsLeft = 3;

  function readLocalProgress() {
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(stored) ? stored : [];
    } catch {
      return [];
    }
  }

  function saveLocalProgress() {
    localStorage.setItem(storageKey, JSON.stringify([...completed].sort((a, b) => a - b)));
  }

  function firstOpenQuestionId() {
    const first = questions.find((question) => !completed.has(question.id));
    return first ? first.id : questions.length + 1;
  }

  function updatePath() {
    const activeId = firstOpenQuestionId();

    steps.forEach((step) => {
      const id = Number(step.dataset.questionId);
      step.classList.toggle("is-complete", completed.has(id));
      step.classList.toggle("is-active", id === activeId);
      step.classList.toggle("is-locked", id > activeId);
    });

    completedCount.textContent = completed.size;
    progressFill.style.width = `${Math.min((completed.size / questions.length) * 100, 100)}%`;
  }

  function questionById(id) {
    return questions.find((question) => question.id === id);
  }

  function openQuestion(id) {
    const activeId = firstOpenQuestionId();
    if (id > activeId) {
      showLockedFeedback(id);
      return;
    }

    activeQuestion = questionById(id);
    heartsLeft = 3;
    level.textContent = activeQuestion.level_title;
    title.textContent = `${activeQuestion.id}. ${activeQuestion.title}`;
    statement.textContent = activeQuestion.statement;
    resetAnswers();
    renderHearts();
    modal.hidden = false;
  }

  function showLockedFeedback(id) {
    const step = steps.find((item) => Number(item.dataset.questionId) === id);
    if (!step) return;
    step.classList.add("is-shaking");
    window.setTimeout(() => step.classList.remove("is-shaking"), 280);
  }

  function closeModal() {
    modal.hidden = true;
    activeQuestion = null;
  }

  function resetAnswers() {
    feedback.hidden = true;
    feedback.classList.remove("is-good", "is-bad");
    continueButton.hidden = true;
    continueButton.textContent = "Continuar";
    answerButtons.forEach((button) => {
      button.disabled = false;
      button.classList.remove("is-correct", "is-wrong");
    });
    rewardText.textContent = "";
  }

  function renderHearts() {
    hearts.forEach((heart, index) => {
      heart.classList.toggle("is-empty", index >= heartsLeft);
    });
  }

  function chooseAnswer(answer) {
    if (!activeQuestion) return;

    const selectedAnswer = answer === "true";
    const isCorrect = selectedAnswer === activeQuestion.answer;
    const selectedButton = answerButtons.find((button) => button.dataset.answer === answer);

    if (isCorrect) {
      answerButtons.forEach((button) => {
        button.disabled = true;
        button.classList.toggle("is-correct", button.dataset.answer === String(activeQuestion.answer));
      });
      completed.add(activeQuestion.id);
      saveLocalProgress();
      updatePath();
      showFeedback(true, activeQuestion.explanation);
      registerCompletion(activeQuestion, selectedAnswer);
      continueButton.hidden = false;
      return;
    }

    heartsLeft = Math.max(heartsLeft - 1, 0);
    renderHearts();
    selectedButton?.classList.add("is-wrong");
    showFeedback(false, heartsLeft > 0 ? "Revise a afirmacao e tente novamente." : activeQuestion.explanation);

    if (heartsLeft === 0) {
      answerButtons.forEach((button) => {
        button.disabled = true;
        button.classList.toggle("is-correct", button.dataset.answer === String(activeQuestion.answer));
      });
      continueButton.textContent = "Recuperar coracoes";
      continueButton.hidden = false;
    }
  }

  function showFeedback(isCorrect, text) {
    feedback.hidden = false;
    feedback.classList.toggle("is-good", isCorrect);
    feedback.classList.toggle("is-bad", !isCorrect);
    feedbackTitle.textContent = isCorrect ? "Resposta correta" : "Ainda nao";
    feedbackText.textContent = text;
  }

  async function registerCompletion(question, answer) {
    try {
      const response = await fetch(completeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          question_id: question.id,
          answer,
        }),
      });

      if (!response.ok) return;

      const data = await response.json();
      if (Array.isArray(data.completed_ids)) {
        completed = new Set([...completed, ...data.completed_ids].map(Number));
        saveLocalProgress();
        updatePath();
      }

      if (data.profile?.coins !== undefined) {
        coins.textContent = data.profile.coins;
      }

      if (data.reward?.xp || data.reward?.coins) {
        rewardText.textContent = `+${data.reward.xp} XP  +${data.reward.coins} moedas`;
      } else {
        rewardText.textContent = "Ponto ja concluido";
      }
    } catch {
      rewardText.textContent = "Progresso salvo neste dispositivo";
    }
  }

  steps.forEach((step) => {
    const button = step.querySelector(".ff-node");
    button.addEventListener("click", () => openQuestion(Number(button.dataset.questionId)));
  });

  answerButtons.forEach((button) => {
    button.addEventListener("click", () => chooseAnswer(button.dataset.answer));
  });

  closeButton.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  continueButton.addEventListener("click", () => {
    if (heartsLeft === 0 && activeQuestion && !completed.has(activeQuestion.id)) {
      heartsLeft = 3;
      resetAnswers();
      renderHearts();
      return;
    }
    closeModal();
  });

  updatePath();
})();

