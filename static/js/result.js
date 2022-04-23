function Result(imgSrc, resultInfo) {
    var node = `<div class="result">
<img src="${imgSrc}" alt="">
<div class="resultInfo">
    <h3>识别结果</h3>
    <div class="info">${resultInfo}</div>
</div>
</div>`
    let result = $(node);
    return result;
}