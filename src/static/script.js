let quizMode = false;
let quizQuestionNumber = 0;
let score = 0;

document.getElementById("quizModeBtn").addEventListener("click", () => {
  quizMode = true;
  document.getElementById("quizModeBtn").classList.add("active");
  document.getElementById("chatModeBtn").classList.remove("active");
  startQuiz();
});

document.getElementById("chatModeBtn").addEventListener("click", () => {
  quizMode = false;
  document.getElementById("chatModeBtn").classList.add("active");
  document.getElementById("quizModeBtn").classList.remove("active");
  addMessageToChat("Chat mode activated 💬", "bot");
});

async function startQuiz() {
  quizQuestionNumber = 0;
  score = 0;
  addMessageToChat("📚 Quiz started! Let's go!", "bot");
  askNextQuestion();
}

async function askNextQuestion() {
  quizQuestionNumber++;

  const prompt = `You are a quiz master. Give me question ${quizQuestionNumber} out of 5 about Python programming.
Return it in this JSON format: 
{"question":"...","options":["A) ...","B) ...","C) ...","D) ..."],"answer":"B"}`;

  const response = await callGeminiAPI(prompt);

  let quiz;
  try {
    quiz = JSON.parse(response);
  } catch {
    addMessageToChat("⚠️ Failed to load quiz question. Try again.", "bot");
    return;
  }

  showQuizQuestion(quiz);
}

function showQuizQuestion(quiz) {
  let html = `<div class="quiz-question">
    <p>${quiz.question}</p>`;

  quiz.options.forEach(opt => {
    html += `<button class="quiz-option" onclick="checkAnswer('${opt.charAt(0)}','${quiz.answer}')">${opt}</button>`;
  });

  html += `</div>`;
  addMessageToChat(html, "bot");
}

function checkAnswer(selected, correct) {
  if (selected === correct) {
    score++;
    addMessageToChat("✅ Correct!", "bot");
  } else {
    addMessageToChat("❌ Wrong! The correct answer was " + correct, "bot");
  }

  if (quizQuestionNumber < 5) {
    askNextQuestion();
  } else {
    addMessageToChat(`🏁 Quiz finished! Your score: ${score}/5`, "bot");
  }
}
