window.onload = () => {

    var poniesPage = 0;
    var poniesBlock = false;

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


    var modifyUserBtnEvent = () => {
        console.log('No user selected');
    }

    var showFatalError = msg => {
        let z = document.createElement('div');
        z.innerHTML = msg;
        z.style.background = '#924';
        z.style.color = '#ddd';
        z.style.position = 'fixed';
        z.style.overflow = 'hidden';
        z.style.textAlign = 'center';
        z.style.padding = '10px 20px';
        z.style.left = '50%';
        z.style.top = '0';
        z.style.fontFamily = 'sans-serif';
        z.style.fontWeight = 'bolder';
        z.style.transform = 'translate(-50%, -100px)';
        document.body.appendChild(z);
        z.animate([{transform: 'translate(-50%, -100px)'},{transform: 'translate(-50%, 30px)'},{transform: 'translate(-50%, 20px)'}],
            {duration: 1200, fill: 'forwards', easing: 'ease-out'});
        setTimeout(() => {
            z.animate([{transform: 'translate(-50%, 20px)'},{transform: 'translate(-50%, 30px)', opacity: 1},
                {transform: 'translate(-50%, -100px)', opacity: 0}], {duration: 900, fill: 'forwards', easing: 'ease-in'});
            setTimeout(() => document.body.removeChild(z), 1100);
        }, 4000);
    }

    var addUserToList = v => {
        let container = document.createElement('div');
        let userData = document.createElement('div');
        let userChange = document.createElement('button');
        let userDelete = document.createElement('button');

        container.style.width = '100%';
        container.style.margin = '5px 0';
        container.style.padding = '5px 0';
        container.style.background = 'rgba(0,0,0,.1)';
        container.style.fontFamily = 'sans-serif';

        let userName = document.createElement('span');
        userName.style.fontWeight = 'bold';
        userName.style.color = '#eee';
        userName.style.display = 'block';
        userName.innerHTML = v.name;
        userData.appendChild(userName);

        let userID = document.createElement('span');
        let userPermission = document.createElement('span');
        userID.style.color = userPermission.style.color = '#ccc';
        userID.style.display = userPermission.style.display = 'block';
        userID.style.fontSize = userPermission.style.fontSize = '.9em';
        userID.innerHTML = `ID: ${v.id}`;
        userPermission.innerHTML = `Perms: ${v.permission_level}`;
        userData.appendChild(userID);
        userData.appendChild(userPermission);

        userChange.style.float = userDelete.style.float = 'right';
        userChange.style.outline = userDelete.style.outline = 'none';
        userChange.style.border = userDelete.style.border = 'none';
        userChange.style.background = userDelete.style.background = 'rgba(0, 0, 0, .2)';
        userChange.style.fontWeight = userDelete.style.fontWeight = 'bold';
        userChange.style.color = userDelete.style.color = '#fff';
        userChange.style.padding = userDelete.style.padding = '9px';
        userChange.style.cursor = userDelete.style.cursor = 'pointer';
        userChange.style.transform = userDelete.style.transform = 'translateY(-140%)';
        userChange.innerHTML = 'Modify';
        userDelete.onclick = deleteUserEvent;
        userDelete.style.marginRight = '10px';
        userDelete.innerHTML = 'Delete';

        userChange.onclick = ev => {
            let userData = ev.target.parentElement.childNodes[0].childNodes;
            let userName = userData[0].innerHTML;
            let userID = userData[1].innerHTML.split(' ')[1];
            let userPermissions = userData[2].innerHTML.split(' ')[1];

            for (let perm of modify_user_form.getElementsByClassName('permission_modify')) {
                let permID = perm.getAttribute('perm');
                perm.checked = (userPermissions & +permID);
                if (+permID === 1)
                    perm.checked = !perm.checked;
            }

            modify_user_info.innerHTML = 'Modifying user <b>' + userName + '</b> with ID ' + userID;

            modify_user_form.style.display = 'block';
            modify_user_form.animate([
                {transform: 'translate(-50%, -50%) scale(.9)'},
                {transform: 'translate(-50%, -50%) scale(1.05)'},
                {transform: 'translate(-50%, -50%) scale(1.04)'},
                {transform: 'translate(-50%, -50%) scale(1)'}
            ], {duration: 450, fill: 'forwards', easing: 'ease-out'});

            modify_user_btn.removeEventListener('click', modifyUserBtnEvent);
            modifyUserBtnEvent = () => {
                console.log('Requesting...');
                let permissionCount = 0;
                for (let perm of modify_user_form.getElementsByClassName('permission_modify')) {
                    let oldCount = permissionCount;
                    if (perm.getAttribute('perm') == '1') {
                        if (perm.checked) {
                            console.log('Blocked! Permissions stay at ' + permissionCount + '. Leaving loop.');
                            break;
                        } else {
                            permissionCount++;
                            console.log('Not blocked, increment 1...: ' + permissionCount);
                        }
                    }
                    permissionCount += perm.checked ? +perm.getAttribute('perm') : 0;
                    console.log('Changed permissions from ' + oldCount + ' to ' + permissionCount);
                }

                fetch('/api/pony', {method: 'PUT', mode: 'same-origin', cache: 'no-cache', headers: {
                    'Content-Type': 'application/json'}, body: JSON.stringify({
                        username: userName, permission_level: permissionCount
                    })}).then(res => res.json()).then(d => {
                        if (d.result != '200') {
                            return showFatalError(d.message);
                        }
                        modify_user_btn.style.background = '#131';
                        modify_user_btn.innerHTML = d.message;
                        setTimeout(() => {
                            modify_user_btn.style.background = 'rgba(0,0,0,.4)';
                            modify_user_btn.innerHTML = 'Change permissions';
                        }, 4000);
                        fetch(`/api/ponies/${poniesPage}`, {mode: 'same-origin', cache: 'no-cache'}).then(res => res.json()).then(d => {
                            user_list.innerHTML = '';
                            poniesPage = 0;
                            poniesBlock = false;
                            printUsers(d);
                        }).catch(err => {
                            console.log(err);
                            showFatalError('Fatal error while updating users');
                        });
                    }).catch(() => showFatalError('Internal Server Error'));
            }
            modify_user_btn.addEventListener('click', modifyUserBtnEvent);

        }

        container.appendChild(userData);
        container.appendChild(userChange);
        container.appendChild(userDelete);
        user_list.appendChild(container);

        return container;
    }

    var printUsers = d => d.users.forEach(v => addUserToList(v));

    add_user_btn.onclick = async () => {
        let username = add_username.value;
        let password = add_password.value;
        let passwordCheck = add_password_check.value;
        let permissionsCount = 1;
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
            permissionsCount += el.checked ? +el.getAttribute('perm') : 0);

        var oldColor = add_user_btn.style.background || 'rgba(0,0,0,.25)';
        fetch(add_user_url, {
            method: 'POST', mode: 'same-origin', cache: 'no-cache', headers: {
                'Content-Type': 'application/json'}, redirect: 'error', body: JSON.stringify({
                    username: username, password: password, permission_level: permissionsCount
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
                    if (d.result == '200') {
                        let container = addUserToList({id: d.id, name: username, permission_level: permissionsCount});
                        container.style.overflow = 'hidden';
                        container.animate([{transform: 'translate(100%, -50%)'}, {transform: 'translateX(-50%, -50%)'}],
                            {duration: 400, fill: 'forwards', ease: 'ease-out'});
                    }
                }).catch(() => {
                    add_user_btn.style.background = '#924';
                    add_user_btn.innerHTML = 'Internal Server Error';
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
                });

    }

    var deleteUserEvent = ev => {
        let n = document.createElement('div');
        let txt = document.createElement('div');
        let yes = document.createElement('button');
        let no = document.createElement('button');

        n.style.position = 'fixed';
        n.style.background = '#446';
        n.style.fontFamily = 'sans-serif';
        n.style.padding = '20px';
        n.style.top = '50%';
        n.style.left = '50%';
        n.style.transform = 'translate(-50%, -50%)';
        n.style.textAlign = 'center';
        n.style.color = '#ddd';

        let username = ev.target.parentElement.childNodes[0].childNodes[0].innerHTML;
        txt.innerHTML = `Are you sure you want to delete ${username}?`;
        n.appendChild(txt);

        yes.style.display = no.style.display = 'inline-block';
        yes.style.outline = no.style.outline = 'none';
        yes.style.border  = no.style.border  = 'none';
        yes.style.padding = no.style.padding = '8px';
        yes.style.margin  = no.style.margin  = '4px';
        yes.style.background = no.style.background = '#556';
        yes.style.color = no.style.color = '#fff';
        yes.innerHTML = 'Yes'; no.innerHTML = 'No';

        yes.onclick = no.onclick = evn => {
            if (evn.target.innerHTML === 'Yes') {
                fetch('/api/pony', {method: 'DELETE', cors: 'same-origin', cache: 'no-cache', headers: {
                    'Content-Type': 'application/json'}, body: JSON.stringify({username: username})}).then(res => res.json()).then(d => {
                        if (d.result == 200)
                            ev.target.parentElement.parentElement.removeChild(ev.target.parentElement);
                        else
                            showFatalError(d.message);
                    });
            }
            document.body.removeChild(n);
        }

        n.appendChild(yes);
        n.appendChild(no);
        document.body.appendChild(n);
    }

    modify_user_form_exit.onclick = () => {
        modify_user_form.style.display = 'none';
    }

    fetch(`/api/ponies/${poniesPage}`, {mode: 'same-origin', cache: 'no-cache'}).then(res => res.json()).then(d => {
        printUsers(d);
    }).catch(err => {
        console.log(err);
        showFatalError('Fatal error while requesting users');
    });

    user_list.onscroll = ev => {
        if (user_list.scrollTop === (user_list.scrollHeight - user_list.offsetHeight) && !poniesBlock) {
            fetch(`/api/ponies/${++poniesPage}`, {mode: 'same-origin', cache: 'no-cache'}).then(res => res.json()).then(d => {
                if (d.users)
                    printUsers(d);
                else
                    poniesBlock = true;
            }).catch(err => {
                console.log(err);
                showFatalError('Fatal error while requesting users');
            });
        }
    }

}