/** @type {import('tailwindcss').Config} */
module.exports = {
    DarkMode: 'class'
    content: [
        "./templates/**/*.html",
        "./**/templates/**/*.html",
        "./**/static/**/*.js",
        "./src/**/*.{html,js,py}",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
}
