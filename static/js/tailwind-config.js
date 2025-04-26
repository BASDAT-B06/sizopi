tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#91986E', 
                    '80': '#91986ECC',    
                    '60': '#91986E99',    
                    '40': '#91986E66',    
                    '20': '#91986E33',    
                },
                secondary: {
                    DEFAULT: '#F5EFE0', 
                    '80': '#F5EEDBCC',    
                    '60': '#F5EEDB99',   
                    '40': '#F5EEDB66',    
                    '20': '#F5EEDB33',    
                },
                accent: {
                    '50': '#FBF0E6',
                    '200': '#FAE9D9',
                    '400': '#F2D4B9',
                    '500': '#DB6900',
                    '600': '#C55F00',
                    '700': '#A44F00',
                    '800': '#A44F00',
                },
                neutral: {
                    'black': '#121212'
                }
            },
            fontFamily: {
                'header': ['Helvetica', 'Arial', 'sans-serif'],
                'body': ['Poppins', 'sans-serif']
            },
            fontSize: {
                'h1': ['72px', {
                    lineHeight: 'normal',
                    fontWeight: '700',
                }],
                'h2': ['60px', {
                    lineHeight: 'normal',
                    fontWeight: '700',
                }],
                'h3': ['48px', {
                    lineHeight: 'normal',
                    fontWeight: '700',
                }],
                'h4': ['36px', {
                    lineHeight: 'normal',
                    fontWeight: '700',
                }],
                'h5': ['30px', {
                    lineHeight: 'normal',
                    fontWeight: '700',
                }],
                'h6': ['24px', {
                    lineHeight: '140%',
                    fontWeight: '700',
                }]
            }
        }
    }
};
