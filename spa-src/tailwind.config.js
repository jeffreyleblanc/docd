import colors from 'tailwindcss/colors'

export default {
    content: [
        './index.html',
        './src/**/*.{vue,js,ts,jsx,tsx}',
    ],
    safelist: [
        'highlighted-syntax'
    ],
    darkMode: 'class',
    theme: {
        extend: {
            // See https://tailwindcss.com/docs/customizing-colors
            colors: {
                core: colors.gray,
                accent: colors.cyan
            }
        },
    },
    variants: {
        extend: {},
    }
}
