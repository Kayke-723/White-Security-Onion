const video = document.getElementById("video")
const canvas = document.getElementById("output")
const ctx = canvas.getContext("2d")
const statusText = document.getElementById("status")

// Nome do usuário (pode ser digitado em um input)
const usernameInput = document.getElementById("username")

const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
})

hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7,
})

let lastGestureData = null

// Callback quando o MediaPipe detecta a mão
hands.onResults((results) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0]
        drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: "#0f0", lineWidth: 2 })
        drawLandmarks(ctx, landmarks, { color: "#f00", lineWidth: 1 })

        // Salva os keypoints como lista [[x,y,z], ...]
        lastGestureData = landmarks.map(p => [p.x, p.y, p.z])
    } else {
        statusText.innerText = "Nenhuma mão detectada"
    }
})

// Função chamada quando o usuário tenta autenticar
async function autenticarPorGesto() {
    if (!lastGestureData) {
        statusText.innerText = "❌ Nenhum gesto detectado"
        return
    }

    const username = usernameInput?.value?.trim() || ""
    if (!username) {
        statusText.innerText = "❌ Digite seu nome de usuário!"
        return
    }

    try {
        const response = await fetch("/api/valida_gesto/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                username,
                keypoints: lastGestureData,
            }),
        })

        const data = await response.json()

        if (data.status === "ok") {
            statusText.innerText = "✅ Login autorizado com gesto!"

            // Aguarda 1 segundo e redireciona para a home
            setTimeout(() => {
                window.location.href = window.APP_HOME_URL || "/home/"
            }, 1000)

        } else {
            statusText.innerText = "❌ " + (data.message || "Gesto não corresponde ao cadastrado.")
        }
    } catch (err) {
        console.error("Erro em autenticarPorGesto:", err)
        statusText.innerText = "Erro na comunicação com o servidor."
    }
}

// Captura CSRF do cookie (necessário no Django)
function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";")
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}

// Iniciar câmera
const camera = new Camera(video, {
    onFrame: async () => await hands.send({ image: video }),
    width: 640,
    height: 480,
})
camera.start()

// Você pode ligar a função autenticarPorGesto() a um botão:
document.getElementById("autenticar").addEventListener("click", autenticarPorGesto)
