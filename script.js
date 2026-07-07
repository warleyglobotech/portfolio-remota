const inputUrl = document.getElementById('inputUrl');
const btnProcessar = document.getElementById('btnProcessar');
const divLoading = document.getElementById('loading');
const areaResultado = document.getElementById('areaResultado');
const textoResultado = document.getElementById('textoResultado');

btnProcessar.addEventListener('click', async () => {
    const url = inputUrl.value.trim();
    if (!url) return;

    areaResultado.classList.add('escondido');
    divLoading.classList.remove('escondido');
    btnProcessar.disabled = true;

    try {
        const response = await fetch('https://portfolio-remota.onrender.com/api/v1/decode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) throw new Error('Erro na API');

        const data = await response.json();
        
        textoResultado.innerText = data.palavra_oculta || data.resultado;
        areaResultado.classList.remove('escondido');
        
    } catch (error) {
        textoResultado.innerText = "Falha ao processar a matriz. Verifique o link.";
        areaResultado.classList.remove('escondido');
    } finally {
        divLoading.classList.add('escondido');
        btnProcessar.disabled = false;
    }
});