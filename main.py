from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import os
import re
import base64

def save_screenshot(driver, file_path, is_full_size=False):
    # スクリーンショット設定
    screenshot_config = {
        # Trueの場合スクロールで隠れている箇所も含める、Falseの場合表示されている箇所のみ
        "captureBeyondViewport": is_full_size,
    }

    # スクリーンショット取得
    base64_image = driver.execute_cdp_cmd("Page.captureScreenshot", screenshot_config)

    # ファイル書き出し
    with open(file_path, "wb") as fh:
        fh.write(base64.urlsafe_b64decode(base64_image["data"]))


# 設定
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ドライバーの生成
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Selenium Gridを利用する場合(デバッグ等で動作見る時はこっち使うとわかりやすい)
# driver = webdriver.Remote(
#     command_executor=os.environ["SELENIUM_URL"],
#     options=options
# )

# 全ての操作にwaitを入れる場合にコメントイン
# driver.implicitly_wait(10)

# マスタデータ (画面からDBに設定できるようにする項目)
targets = [
    {
        "name": "楽天",
        "keywords": ["スイッチボット", "k10+", "pro"],
        "url": "https://www.rakuten.co.jp/",
        "input-xpath": "//*[@id=\"common-header-search-input\"]",
        "submit-type": 'click',
        "submit-xpath": "//*[@id=\"wrapper\"]/div[5]/div/div/div/div[1]/div/div/div/a",
        "items-xpath": "//*[@id=\"root\"]/div[3]/div[2]/div[5]/div/div/div/div",
        "title-xpath": ["div[2]/h2/a"],
        "title-ignore": ["[PR]", "アクセサリー"],
        "value-xpath": ["div[3]/div[1]/div"],
        "link-xpath": ["div[2]/h2/a"],
    },
    {
        "name": "Amazon",
        "keywords": ["switchbot", "k10+", "pro"],
        "url": "https://www.amazon.co.jp/",
        "input-xpath": '//*[@id="twotabsearchtextbox"]',
        "submit-type": 'submit',
        "submit-xpath": '//*[@id="nav-search-submit-button"]',
        "items-xpath": '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div',
        "title-xpath": [
            'div/div/span/div/div/div[2]/div[1]/h2/a/span',
            'div/div/span/div/div/div[3]/div[1]/h2/a/span'
        ],
        "title-ignore": ["スポンサー", "アクセサリー"],
        "value-xpath": [
            'div/div/span/div/div/div[2]/div[3]/div[1]/div[1]/a/span/span[2]',
            'div/div/span/div/div/div[3]/div[3]/div[1]/div[1]/a/span/span[2]',
        ],
        "link-xpath": [
            'div/div/span/div/div/div[2]/div[1]/h2/a',
            'div/div/span/div/div/div[3]/div[1]/h2/a'
        ],
    }

]


for target in targets:
    print(target["name"])
    driver.get(target["url"])
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)

    # キーワードで検索
    keyword = " ".join(target["keywords"])
    driver.find_element(By.XPATH, target["input-xpath"]).send_keys(keyword)
    if target['submit-type'] == 'submit':
        result = driver.find_element(By.XPATH, target["submit-xpath"]).submit()
    elif target['submit-type'] == 'click':
        result = driver.find_element(By.XPATH, target["submit-xpath"]).click()
    else:
        # print("No such search button")
        break

    # 描画されるまで待機 (debugの際はコメントアウト推奨)
    WebDriverWait(driver, 45).until(EC.presence_of_all_elements_located)
    # キャプチャ取得 (debug時はコメントアウト推奨)
    save_screenshot(driver, "outputs/"+target["name"]+".png", is_full_size=True)

    # 検索後のページタイトル
    # print(driver.title)

    # 検索結果のリスト取得
    items = driver.find_elements(By.XPATH, target["items-xpath"])

    for item in items:
        ignore = False

        # Amazonのおすすめ がついてる場合に構造が変わるため、第二候補を設定できるように実装
        for tpath in target['title-xpath']:
            try:
                # タイトル取得
                title_element = item.find_element(By.XPATH, tpath)
                title = title_element.get_attribute('innerHTML')
                break
            except Exception:
                # 取得エラーの場合は次のxpathでリトライ
                continue
        else:
            # タイトルが取得できなかったら次のitemへ
            continue
            
        # タイトルに除外キーワードが含まれていたらスキップ
        for txt in target["title-ignore"]:
            if txt.lower() in title.lower():
                ignore = True
                break
        # タイトルにキーワードが含まていなかったらスキップ (全然関係ない商品が撮れることがあったので...)
        for key in target["keywords"]:
            if key.lower() not in title.lower():
                ignore = True
                break

        if not ignore:
            # Amazonのおすすめ がついてる場合に構造が変わるため、第二候補を設定できるように実装)
            for vpath in target['value-xpath']:
                try:
                    # 値の取得
                    value_element = item.find_element(By.XPATH, vpath)
                    value = value_element.get_attribute('innerHTML')
                    break
                except Exception as e:
                    # 取得エラーの場合は次のxpathでリトライ
                    continue
            else:
                # 値が取得できなかったら次のitemへ
                continue

            #子要素が混ざっている場合があるのでHTMLタグを除去
            value = re.sub(re.compile('<.*?>'), '', value)
            #数値のみに
            value = re.sub(r'\D', '', value)

            # Amazonのおすすめ がついてる場合に構造が変わるため、第二候補を設定できるように実装)
            for upath in target["link-xpath"]:
                try:
                    # 詳細ページのURL取得
                    url_element = item.find_element(By.XPATH, upath)
                    url = url_element.get_attribute('href')
                    break
                except Exception as e:
                    # 取得エラーの場合は次のxpathでリトライ
                    continue
            else:
                # 値が取得できなかったら次のitemへ
                continue

            # 取得結果をアウトプット
            print('----------')
            print(f"{value}")
            print(f"{title}")
            print(f"{url}")
            print('----------')
            break
    else:
        print("No such items element")

else:
    # 終了
    driver.quit()
