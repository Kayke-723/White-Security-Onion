const video = document.getElementById("video")
const output = document.getElementById("output")
const drawCanvas = document.getElementById("drawCanvas")
const ctxOutput = output.getContext("2d")
const ctxDraw = drawCanvas.getContext("2d")
const statusText = document.getElementById("status")

const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
})

hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7,
})

let bothHandsOpenStart = null

// 🔹 Detecta se a palma está aberta
function isPalmOpen(landmarks) {
    const wrist = landmarks[0]
    const middleTip = landmarks[12]
    return Math.hypot(wrist.x - middleTip.x, wrist.y - middleTip.y) > 0.25
}

// 🔹 Detecta se a palma está fechada
function isPalmClosed(landmarks) {
    const wrist = landmarks[0]
    const middleTip = landmarks[12]
    return Math.hypot(wrist.x - middleTip.x, wrist.y - middleTip.y) < 0.1
}

hands.onResults((results) => {
    ctxOutput.clearRect(0, 0, output.width, output.height)

    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
        statusText.innerText = "Nenhuma mão detectada."
        return
    }

    // Desenha as conexões e pontos
    results.multiHandLandmarks.forEach((landmarks, i) => {
        drawConnectors(ctxOutput, landmarks, HAND_CONNECTIONS, { color: i === 0 ? "#0ff" : "#f0f", lineWidth: 2 })
        drawLandmarks(ctxOutput, landmarks, { color: i === 0 ? "#0ff" : "#f0f", lineWidth: 1 })
    })

    let leftHand = null, rightHand = null
    results.multiHandedness.forEach((h, i) => {
        if (h.label === "Left") leftHand = results.multiHandLandmarks[i]
        else rightHand = results.multiHandLandmarks[i]
    })

    // 🔹 Mão direita = desenhar
    if (rightHand && isPalmClosed(rightHand)) {
        const rightIndex = rightHand[8]
        const x = (1 - rightIndex.x) * drawCanvas.width
        const y = rightIndex.y * drawCanvas.height

        ctxDraw.strokeStyle = "#00ffcc"
        ctxDraw.lineWidth = 5
        ctxDraw.lineCap = "round"

        ctxDraw.beginPath()
        ctxDraw.lineTo(x, y)
        ctxDraw.stroke()

        statusText.innerText = "✏️ Desenhando com a mão direita..."
    }

    // 🔹 Mão esquerda = apagar
    if (leftHand && isPalmClosed(leftHand)) {
        const leftIndex = leftHand[8]
        const x = (1 - leftIndex.x) * drawCanvas.width
        const y = leftIndex.y * drawCanvas.height

        ctxDraw.clearRect(x - 20, y - 20, 40, 40)
        statusText.innerText = "🧽 Apagando com a mão esquerda..."
    }

    // 🔹 Ambas as mãos abertas = salvar automaticamente
    if (leftHand && rightHand && isPalmOpen(leftHand) && isPalmOpen(rightHand)) {
        if (!bothHandsOpenStart) bothHandsOpenStart = Date.now()
        const duration = (Date.now() - bothHandsOpenStart) / 1000
        statusText.innerText = `💾 Salvando em ${Math.max(0, 5 - duration).toFixed(1)}s...`

        if (duration >= 5) {
            saveDrawing()
            bothHandsOpenStart = null
        }
    } else {
        bothHandsOpenStart = null
    }
})

// 🔹 Inicializa a câmera
const camera = new Camera(video, {
    onFrame: async () => await hands.send({ image: video }),
    width: 960,
    height: 720,
})
camera.start()

// 🔹 Salvar desenho no banco
function saveDrawing() {
    // 🔹 Cria um canvas temporário com fundo branco
    const whiteCanvas = document.createElement("canvas")
    whiteCanvas.width = drawCanvas.width
    whiteCanvas.height = drawCanvas.height
    const ctxWhite = whiteCanvas.getContext("2d")

    // 🔹 Preenche fundo branco
    ctxWhite.fillStyle = "#ffffff"
    ctxWhite.fillRect(0, 0, whiteCanvas.width, whiteCanvas.height)

    // 🔹 Desenha o conteúdo do canvas original
    ctxWhite.drawImage(drawCanvas, 0, 0)

    // 🔹 Converte em imagem Base64
    const dataURL = whiteCanvas.toDataURL("image/png")

    fetch("{% url 'salvar_desenho' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}",
        },
        body: JSON.stringify({ imagem: dataURL }),
    })
        .then((r) => r.json())
        .then((data) => {
            statusText.innerText = "✅ " + data.mensagem
            ctxDraw.clearRect(0, 0, drawCanvas.width, drawCanvas.height)
        })
        .catch(() => {
            statusText.innerText = "❌ Erro ao salvar o desenho."
        })
}


// 🔹 Botões manuais
document.getElementById("salvar").addEventListener("click", saveDrawing)
document.getElementById("limpar").addEventListener("click", () => {
    ctxDraw.clearRect(0, 0, drawCanvas.width, drawCanvas.height)
    statusText.innerText = "🧼 Tela limpa."
})

// 🔹 Pega o CSRF do cookie (Django)
function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";")
        for (let cookie of cookies) {
            cookie = cookie.trim()
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}
