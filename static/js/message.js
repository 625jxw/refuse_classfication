let TOP = 25;
const successNode = `<div class="messagebox success-message animate__animated">
    <span class="message-icon">
        <img src="/static/font/success.svg" alt="">
    </span>
    <span class="message"></span>
    </div>`;
const errorNode = `<div class="messagebox error-message animate__animated">
<span class="message-icon">
    <img src="/static/font/error.svg" alt="">
</span>
<span class="message"></span>
</div>`;
class Message {
    eid = new Date().getTime();
    height = 48
    constructor(message, type) {
        this.width = 22 + message.length * 14;
        if(type == "success") {
            this.messageNode = $(successNode);
        } else if(type == "error") {
            this.messageNode = $(errorNode);
        }
        this.messageNode.attr("id", "message" + this.eid);
        this.messageNode.children(".message").text(message);
        this.messageNode.css({"top":TOP + "px", "margin-left": -(this.width / 2)});
        this.messageNode.addClass("animate__fadeInDown")
    }
    show() {
        $("html").append(this.messageNode);
        TOP += this.height;
        var node = $("#message" + this.eid);
        var timer1 = setTimeout(() => {
            $(node).removeClass("animate__fadeInDown");
            $(node).addClass("animate__fadeOutUp");
            TOP = (TOP < 45) ? 45 : TOP - this.height;
            clearTimeout(timer1);
        }, 1500);
        var timer2 = setTimeout(() => {
            $(node).remove();
            clearTimeout(timer2);
        }, 2000);
    }
}


