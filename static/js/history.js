$(function() {
    /**
     * 垃圾代码不要看了^_^.......
     */
   (() => {
        var t;
        function finish() {
            $(".mycircle").hide();
            clearTimeout(t);
        }
        function wait() {
            $(".mycircle").show();
            t = setTimeout(() => {
                finish();
                new Message("可能服务器出问题了", "error").show();
            }, 15000);
        }
        function His(id, r, img, t) {
            var url = "/static/img_name/" + img;
            var e = `<div class="history" id="${id}">
            <div class="left">
                <img src="${url}" alt="">
            </div>
            <div class="right">
                <div class="result">${r}</div>
                <div class="time">${t}</div>
            </div>
            <div class="delete">
                <img src="/static/font/delete.svg" alt="">
            </div>
        </div>`
            var e1 = $(e);
            var e2 = $(e1).children(".delete");
            $(e2).on("click", () => {
                let _id = id;
                $.get("/delete", {"id":_id}, (data) => {
                    if (data["status"]) {
                        new Message("删除成功", "success").show();
                        $("#" + _id).remove();
                    }
                });
            });
            return e1;
        }

        var name = $.cookie("username");
        var d = $(".deleteAllHistory");
        var u = $("#username");
        if (name) u.html(name);
        var h = $(".historyList");
        $(d).on("click", () => {
            var f = window.confirm("确定删除全部记录?");
            if (f) {
                $.get("/deleteAll", {"username": name}, (data) => {
                    if (data["status"]) {
                        new Message("删除成功", "success").show();
                        setTimeout(() => {
                            location.reload();
                        }, 800);
                    }
                });
            }
        });
        wait();
        $.ajax({
            url:"/history",
            method:"GET",
            data:{"username":name},
            success:function(data) {
                data = JSON.parse(data);
                $(h).empty();
                for (let his of data) {
                    var id = his["id"];
                    var r = his["image_rec"];
                    var t = his["datatime"];
                    var i = his["user_img"]
                    var e = His(id, r, i, t);
                    $(h).append(e);
                }
                finish();
            },
            error:function(data) {
                new Message("获取历史记录失败", "error").show();
            }
        });
    })();
});
