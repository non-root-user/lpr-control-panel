window.onload = () => {

    add_user_btn.onclick = () => {
        if(add_password.value === add_password_check.value){
            if(!isNaN(add_permission_level.value) && (add_permission_level.value & 1)){
                fetch(add_user_url, {
                    method: 'POST',
                    mode: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                       username: add_username.value,
                       password: add_password.value,
                       permission_level: add_permission_level.value
                    })
                });
            }
            else showError("Invalid permission value")
        }
        else showError("Passwords do not match")  
    }

    del_user_btn.onclick = () => {
        
        fetch(delete_user_url, {
            method: 'DELETE',
            mode: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: del_username.value,
            })
        });
    }

    add_user_btn.onclick = async () => {
        let username = add_username.value;
        let password = add_password.value;
        let passwordCheck = add_password_check.value;
        let permissions = 1;
        var oldValBtn = add_user_btn.innerHTML;
        add_user_btn.disabled = true;
        add_user_btn.innerHTML = '.';
        let btnInterval = setInterval(async () => {
            for (let i = 0; i < 3; i++) {
                await new Promise(res => setTimeout(res, 500));
                if (i > 2 || i === 0) add_user_btn.innerHTML='.';
                else add_user_btn.innerHTML += ' .';
            }
        }, 500 * 3);

        await [].forEach.call(document.getElementsByClassName('permission_select'), el =>
            permissions += el.checked ? +permissions.getAttribute('perm') : 0);

        var oldColor = add_user_btn.style.background || 'rgba(0,0,0,.25)';
        fetch(add_user_url, {
            method: 'POST', mode: 'same-origin', cache: 'no-cache', headers: {
                'Content-Type': 'application/json'}, redirect: 'error', body: JSON.stringify({
                    username: username, password: password, permission_level: permissions
                })}).then(res => res.json()).then(d => {
                    clearInterval(btnInterval);
                    add_user_btn.disabled = false;
                    add_user_btn.innerHTML = d.message
                    add_user_btn.style.background = d.result == '200' ? '#264' : '#624';
                    add_user_btn.animate([{transform: 'translateX(-50%) scale(1)'},
                        {transform: 'translateX(-50%) scale(1.06)'},{transform: 'translateX(-50%) scale(1.04)'}],
                        {fill: 'forwards', duration: 750, easing: 'ease'});
                    setTimeout(() => {
                        add_user_btn.style.background = oldColor;
                        add_user_btn.innerHTML = oldValBtn;
                        add_user_btn.animate([{transform: 'translateX(-50%) scale(1.04)'},{transform: 'translateX(-50%) scale(1)'}],
                            {fill: 'forwards', duration: 900});
                    }, 6000);
                }).catch(() => {
                    add_user_btn.style.background = '#924';
                    add_user_btn.innerHTML = 'Interval Server Error';
                    add_user_btn.disabled = false;
                    add_user_btn.animate([{transform: 'translateX(-50%) scale(1)'},
                        {transform: 'translateX(-50%) scale(1.06)'},{transform: 'translateX(-50%) scale(1.04)'}],
                        {fill: 'forwards', duration: 750, easing: 'ease'});
                    setTimeout(() => {
                        add_user_btn.style.background = oldColor;
                        add_user_btn.innerHTML = oldValBtn;
                        add_user_btn.animate([{transform: 'translateX(-50%) scale(1.04)'},{transform: 'translateX(-50%) scale(1)'}],
                            {fill: 'forwards', duration: 900});
                    }, 6000);
                })
        
    }

}