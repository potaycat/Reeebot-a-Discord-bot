KEM_HELP = """CrosskemonoB型號，在生成kemono風格的獸人角色有優勢，即使不使用kemono的hypernetwork的情況下，也很容易生成kemono風格的獸人，缺點是在生成人類的時候，會帶一點獸的元素進去。

示例圖像均沒有使用kemono的hypernetwork。

示例圖像存在部分構圖扭曲的情況，因為是隨便挑選的，4個型號所使用的示例圖像的seed和prompt均為一致，僅用以型號對比參考。

Defaults: 
    negative_prompt="(EasyNegative:1.0),(worst quality, low quality:1.4)",
    sampling_method: "DPM++ 2M Karras",
    steps: int = 20,
    cfg_scale: float = 7.5,
    seed: int = randint(1, 999999999),
"""
