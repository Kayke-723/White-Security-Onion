// Seleciona todas as "onions"
const onions = document.querySelectorAll(".onion")

onions.forEach((onion) => {
    onion.addEventListener("click", (e) => {
        const isLink = onion.classList.contains("onion-link")
        if (isLink) e.preventDefault()

        // Desativa todas as onions
        onions.forEach((o) => {
            o.classList.remove("active")
            o.classList.add("inactive")
            o.querySelector(".content").classList.add("pointer-events-none")
        })

        // Ativa a onion clicada
        onion.classList.remove("inactive")
        onion.classList.add("active")
        onion.querySelector(".content").classList.remove("pointer-events-none")

        // Redireciona caso seja link
        if (isLink) {
            const href = onion.getAttribute("href") || onion.dataset.target
            setTimeout(() => {
                if (href) window.location.href = href
            }, 250)
        }
    })
})