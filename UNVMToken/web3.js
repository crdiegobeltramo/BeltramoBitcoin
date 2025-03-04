async function connectWallet() {
    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            document.getElementById("walletAddress").innerText = `Wallet: ${accounts[0]}`;
        } catch (error) {
            console.error("Acceso denegado", error);
        }
    } else {
        alert("Metamask no detectado. Instálalo para continuar.");
    }
}
