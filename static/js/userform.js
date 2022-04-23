/**
 * 垃圾代码别看了^_^
 */
$(function() {
    function userSign() {
        const signName = $("#signname");
        const password = $("#signpassword");
        const p2 = $("#checkPwd");
        const e1 = $(".signnameError");
        const e2 = $(".signnameExist");
        const e3 = $(".passwordError");
        const e4 = $(".pwdCheckError");
        const eye1 = $("#eye1");
        const eye2 = $("#eye2");
        function showError(v1, v2) {
            //输入框
            $(v1).addClass("input-error");
            //错误信息
            $(v2).css("display", "block");
        }
        function removeError(v1, v2) {
            $(v1).removeClass("input-error");
            $(v2).css("display", "none");
        }
        function checkLength() {
            var value = signName.val().replaceAll(" ", "");
            signName.val(value);
            if (value.length >= 4 && value.length <= 8) {
                return true;
            }
            showError(signName, e1);
            return false;
        }
        function checkPassword() {
            var s2 = /[\u4e00-\u9fa5]/;
            var s3 = /[\s]/;
            var value = $(password).val();
            if (value.length < 6 || value.length > 20) {
                console.log(value.length);
                showError(password, e3);
                return false;
            }
            if (s2.test(value) || s3.test(value)) {
                showError(password, e3);
                return false;
            }
            return true;
        }
        function isValidPassword() {
            return checkPassword();
        }
        function checkTwice() {
            var val1 = $(password).val();
            var val2 = $(p2).val();
            if (val1 != val2) {
                $(password).addClass("input-error");
                showError(p2, e4);
                return false;
            } else {
                removeError(password, e3);
                return true;
            }
            
        }
        var isExist = false;
        function checkExist() {
            var name = $(signName).val();
            var path = "/isExist";
            $.get(path, {"username": name}, function (data) {
                console.log(data);
                if (data["isExist"]) {
                    showError(signName, e2);
                    isExist = true;
                }
            });
            return isExist;
        }
        function isValidSignName() {
            if (!checkExist()) {
                return checkLength();
            }
            return false;
        }
        function doSign() {
            var message = new Message("注册成功", "success");
            var message2 = new Message("注册失败, 可能服务器出问题了", "error");
            if ($(".signForm .input-error").eq(0) == null)
                return false;
            if (isExist || !checkLength() || !isValidPassword() || !checkTwice()) {
                return false;
            }
            var api = "/register";
            $.ajax({
                url: api,
                method:"post",
                data: {
                    "username": signName.val(),
                    "password": password.val(),
                    "repassword": p2.val()
                },
                success: function(data) {
                    if (data["status"] == 200) {
                        message.show();
                        userForm.login.click();
                        $("#loginusername").val(signName.val());
                    } else {
                        message2.show();
                    }
                },
                error: function (data) {
                    message2.show();
                }
            });
        }
        function watch() {
            $(signName).focus(function () {
                $("#tip1").css("display", "block");
                removeError(signName, e1);
                removeError(signName, e2);
            });
            $(signName).blur(function () {
                $("#tip1").css("display", "none");
                isValidSignName();
            });
            $(password).focus(function () {
                $("#tip2").css("display", "block");
                removeError(password, e3);
                removeError(p2, e4);
            });
            $(password).blur(function () {
                $("#tip2").css("display", "none");
                isValidPassword();
            });
            $(p2).focus(function () {
                removeError(p2, e4);
            });
            $(p2).blur(function () {
                checkTwice();
            });
            $("#signButton").click(function () {
                if (doSign() === false) {
                    new Message("请检查输入是否合法!", "error").show();
                }
            });
            $(eye2).click(() => {
                $(password).attr("type", "text");
                $(eye2).hide();
                $(eye1).css("display", "inline-block");
            });
            $(eye1).click(() => {
                $(password).attr("type", "password");
                $(eye1).hide();
                $(eye2).css("display", "inline-block");
            });
        }
        watch();
    }

    const userForm = {
        a: $("#unlogin"),
        coverpage : $(".coverpage"),
        userform : $("#userform"),
        cancel: $("#userform .cancel"),
        login: $("#userform .login"),
        sign: $("#userform .sign"),
        loginForm: $("#userform .loginForm"),
        signForm: $("#userform .signForm"),
        showLoginForm: function() {
            $(this.signForm).hide();
            $(this.loginForm).show(350);
        },
        showSignForm: function() {
           $(this.loginForm).hide();
           $(this.signForm).show(350);
        }
    };

    $(userForm.a).click(function() {
        this.preventDefault = true;
        $(userForm.coverpage).show();
        $(userForm.userform).css("display", "block");
        $(userForm.userform).removeClass("animate__fadeOutUp");
        $(userForm.userform).addClass("animate__fadeInDown");
        userForm.showLoginForm();
    });
    $(userForm.cancel).click(function() {
        $(userForm.userform).removeClass("animate__fadeInDown");
        $(userForm.userform).addClass("animate__fadeOutUp");
        $(userForm.coverpage).hide();                              
        var timer = setTimeout(() => {
            $(userForm.userform).css("display", "none");
            clearTimeout(timer);
        }, 500);
    });


    function clearForm() {
        $("#loginname").val("");
        $("#loginpassword").val("");
        $("#signname").val("");
        $("#signpassword").val("");
        $("#checkPwd").val("");
    }
    $(userForm.login).click(function() {
        clearForm();
        $(this).css("color", "#333");
        $(userForm.sign).css("color", "#007aff");
        userForm.showLoginForm();
    });
    
    $(userForm.sign).click(function() {
        clearForm();
        $(this).css("color", "#333");
        $(userForm.login).css("color", "#007aff");
        userForm.showSignForm();
    });

    function userLogin() {
        var username = $("#loginusername").val();
        var password = $("#loginpassword").val();

        if(username.length == 0 || password.length == 0) {
            new Message("用户名或密码不合法", "error").show();
            return;
        }
        var path = "/login";
        $.ajax({
            url: path,
            method: "POST",
            data: {
                "username": username,
                "password": password,
            },
            success: function(data, status, xhr) {
                if (data["status"] === 200) {
                    new Message("登录成功", "success").show();
                    var timer = setTimeout(() => {
                        location.reload();
                        clearTimeout(timer);
                    }, 200);
                } else {
                    new Message("用户名或密码错误", "error").show();
                }
            },  
            error: function(data, status, xhr) {
                    new Message("服务器出错了", "error").show();
                }
            }
        );
    }
    ;(function() {
        userSign();
        $("#loginButton").click(function() {
            userLogin();
        });
    })();
});