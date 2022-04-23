$(function() {
    /*
    垃圾代码不要看了^_^
    */
    ;(function() {
        const logined = $("#logined");
        $(logined).mouseenter(() => {
            $("#logout").css("display", "inline-block");
        });
    
        $(logined).mouseleave(() => {
            $("#logout").css("display", "none");
        });
        $("#logout").click(() => {
            $.ajax({
                url:"/logout",
                method:"GET",
                success:(data) => {
                    if (data["status"]) {
                        new Message("退出成功", "success").show();
                        $(logined).children(".username").text("");
                        $(logined).css("display", "none");
                        $("#unlogin").css("display", "inline-block");
                        var t = setTimeout(() => {
                            location.reload();
                            clearTimeout(t);
                        }, 500);
                    } else {
                        new Message("退出失败", "error").show();
                    }
                },
                error: () => {
                    new Message("退出失败", "error").show();
                }
            });
        });
        $("#myhome").click(() => {
            if ($.cookie("username")) {
                location.href = location.href + "/home";
            } else {
                $("#unlogin").click();
            }
        });
        var username = $.cookie("username");
        if (username) {
            $("#unlogin").css("display", "none");
            $(logined).css("display", "inline-block");
            $(logined).children(".username").text(username);
        }
    })();
    if (!$.cookie("username")) {
        $("#unlogin").click();
    }
    (function() {
        const menuItems = $(".menu .item");
        const contentboxs = $(".main-content .content-box");
        let pre = 0;
        for (let i = 0; i < menuItems.length; i++) {
            menuItems.eq(i).click(function() {
                menuItems.eq(pre).removeClass("clicked");
                $(this).addClass("clicked");
                contentboxs.eq(pre).addClass("hidden");
                contentboxs.eq(i).removeClass("hidden");
                var offset = $(this).offset().top;
                $("#garbage-recognition").addClass("hidden");
                window.scrollTo(0, offset);
                pre = i;
            });
        }
        const mainapi = $(".mainapi");
        mainapi.click(function() {
            if (!$.cookie("username")) {
                window.scrollTo(0, 0);
                $("#unlogin").click();
                return;
            }
            $(menuItems).removeClass("clicked");
            contentboxs.addClass("hidden");
            $("#garbage-recognition").removeClass("hidden");
            var offset = $(this).offset().top;
            window.scrollTo(200, offset);
        });
    })();
    ;(function() {
        const fileMap = new Map();
        const b = $(".showimg");
        const f = $("#imgFile");
        const u = $("#upload");
        const d = $("#deleteAll");
        const c = $("#chooseImg");
        function isExist(name) {
            return fileMap.has(name);
        }
        function deleteImage(id) {
            revokeObjectURL($(id).attr("src"));
            fileMap.delete(id);
            console.log(fileMap.size);
            console.log(id);
            $("#" + id).remove();
        }
        function deleteAll() {
            fileMap.clear();
            $(b).empty();
            $(".info").css("opacity", "1");
        }
        function getImages() {
            if (fileMap.size == 0) return null;
            var formData =  new FormData();
            fileMap.forEach((value, key) => {
                console.log(key);
                formData.append("images", value, value.name);
            });
            return formData;
        }
        var t;
        function finish() {
            $(".coverpage").hide();
            $(".mycircle").hide();
            clearTimeout(t);
        }
        function wait() {
            $(".coverpage").show();
            $(".mycircle").show();
            t = setTimeout(() => {
                finish();
                new Message("可能服务器出问题了", "error").show();
            }, 15000);
        }
        function upload() {
            var path = "/photo_rec";
            var images = getImages();
            if (images == null) {
                new Message("请选择图片", "error").show();
                return;
            }
            wait();
            $.ajax(
               {
                    url: path,
                    type: "POST",
                    contentType : false,
                    processData:false,
                    data: images,
                    success: function(data) {
                        let resultList = $(".resultList");
                        data = JSON.parse(data);
                        resultList.empty();
                        fileMap.forEach((value, key) => {
                            var result = data[key];
                            var src = creatObjectURL(value);
                            resultList.append(Result(src, result));
                        });
                        new Message("识别成功", "success").show();
                        finish();
                    },
                    error: function (data) {
                        new Message("识别失败，请再试一次", "error").show();
                        var t1 = setTimeout(() => {
                            finish();
                            clearTimeout(t1);
                        }, 1000);
                    }
               }
            );
        }
        function creatObjectURL(file) {
            if (window.URL) {
                return window.URL.createObjectURL(file);
            } else if (window.webkitURL) {
                return window.webkitURL.createObjectURL(file);
            } else {
                return null;
            }
        }
        function revokeObjectURL(url) {
            if (window.URL) {
                return window.URL.revokeObjectURL(url)
            } else {
                return window.webkitURL.revokeObjectURL(url)
            }
        }
        function convertName(name) {
            return md5(name);
        }
        function createImgNode(id, src) {
            var $img = $("<img>");
            $img.attr("src", src);
            if (id != 0) {
                $img.attr("id", id);
                $($img).on("click", (event) => {
                    event.stopPropagation();
                    var e = window.confirm("确定删除?");
                    if (e) {
                        deleteImage(id);
                    }
                });
            }
            return $img;
        }
        b.click(() => {
            if (fileMap.size == 10) {
                new Message("最多选择十张图片", "error").show();
                return;
            }
            $(f).click();
        });
        d.click(function() {
            console.log("deleteAll");
            deleteAll();
        });

        $(u).on("click", function() {
            upload();
        });
        $(c).click(() => {
            if (fileMap.size == 10) {
                new Message("最多选择十张图片", "error").show();
                return;
            }
            $(f).click();
        });
        $(f).change(function(event) {
            var m = 2097152;
            let files = event.target.files;
            if (files.length == 0) return;
            $(".info").css("opacity", "0.3");
            for (let image of files) {
                if (fileMap.size == 10) break;
                if (image.size > m) continue;
                var id = convertName(image.name);
                if (isExist(id)) {
                    new Message("图片名称不能一样", "error").show();
                    continue;
                }
                var src = creatObjectURL(image);
                fileMap.set(id, image);
                var img = createImgNode(id, src);
                $(b).append(img);
            }          
        });
    })();
});