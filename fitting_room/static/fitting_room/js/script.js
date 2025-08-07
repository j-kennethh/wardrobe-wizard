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

    const btn = document.getElementById('new-item-form-button');
    if (btn) {
        btn.addEventListener('click', function () {
            console.log("Add item was clicked");

            // create transluscent loading overlay
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';

            // Create spinner from scratch (cant find API)
            const spinner = document.createElement('div');
            spinner.style.border = '5px solid #f3f3f3';
            spinner.style.borderTop = '5px solid #3498db';
            spinner.style.borderRadius = '50%';
            spinner.style.width = '50px';
            spinner.style.height = '50px';
            spinner.style.animation = 'spin 1s linear infinite';

            // Add spinner to overlay
            overlay.appendChild(spinner);

            // Add overlay to body
            document.body.appendChild(overlay);

            // CSS animation of 
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        });
    }

});