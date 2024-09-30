// const URL_BASE = "http://127.0.0.1:5000/"
$(document).on("DOMContentLoaded", async () => {

    const JSONHEADERS = {
        "Content-Type" : "application/json",
        "mimetype": "application/json"
    };

    const createMsgWithClass = (msg, cls) => {
        const msg_container = $( "<div/>", {"class": "message"} );
        msg_container.addClass(cls);
        $( "<div/>", {text: msg}).appendTo(msg_container);
        $("#chatPane").append(msg_container);
    };

    await fetch("/clients", {
        method: "GET",
        headers: JSONHEADERS
    }).then(async (response) => {
        let clients = await response.json();
        clients.forEach(client => {
            $( "<option/>", {
                "value": btoa(client.display_name),
                html: client.display_name
            }).appendTo( "#clientSelector" );
        });
    }, (rejection) => {
        console.log(rejection);
        alert("encountered error fetching clients! See console for details")
    });

    $("#selectClientBtn").on("click", async () => {
        const client = atob($("#clientSelector").val());

        await fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ client }),
            headers: JSONHEADERS
        }).then(async (response) => {
            let chat = await response.json();
            $("#clientSelectionContainer").prop("hidden", true);
            $("#chat").prop("hidden", false);
            $("#chat").attr("uuid", chat.uuid)
        }, (rejection) => {
            console.log(rejection);
            alert("encountered error selecting a client! See console for details")
        });
    });

    $("#sendUserMessageBtn").on("click", async () => {
        const user_message = $("#userMessageBox").val();
        const uuid = $("#chat").attr("uuid");

        createMsgWithClass(user_message, "selfMessage");
        $("#userMessageBox").val("");

        await fetch("/chat", {
            method: "PUT",
            body: JSON.stringify({ uuid, user_message }),
            headers: JSONHEADERS
        }).then(
            async (response) => {
                let chat = await response.json();
                const msgs = chat.messages
                const last_msg = msgs[msgs.length-1].content;
                createMsgWithClass(last_msg, "otherMessage");
            },
            (rejection) => {
                console.log(rejection);
                alert("failed to send a new message! See console for details");
            }
        );
    });
});
