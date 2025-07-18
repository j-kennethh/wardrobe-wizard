document.addEventListener('DOMContentLoaded', function () {
    // Screenshot functionality
    if (document.getElementById('screenshot')) {
        document.getElementById('screenshot').addEventListener('click', function () {
            const element = document.getElementById('capture');

            html2canvas(element).then(canvas => {
                const resultDiv = document.getElementById('screenshot-result');
                resultDiv.innerHTML = '';
                resultDiv.appendChild(canvas);

                // download screenshot
                // const downloadBtn = document.createElement('a');
                // downloadBtn.href = canvas.toDataURL('image/png');
                // downloadBtn.download = 'screenshot.png';
                // downloadBtn.className = 'btn btn-success mt-2';
                // downloadBtn.textContent = 'Download Image';
                // resultDiv.appendChild(downloadBtn);
            });
        });
    }

});