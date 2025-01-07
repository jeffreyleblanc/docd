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
                core: colors.zinc,
                dkaccent: colors.blue,
                ltaccent: colors.sky
            }
        },
    },
    variants: {
        extend: {},
    }
}
