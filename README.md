# AutoSubmit

## Usage

1. Set your account in `user.json` and place it under `assets` folder. The format must be:

    ```json
    {
        "loginName": "<YOUR USERNAME>",
        "loginPassword": "<YOUR PASSWORD>",
        "loginTerminalType": 10,
        "isCarryOn": 1
    }
    ```

2. Recognize table data using Tencent QQ (Alt + Ctrl + O) or something else, and save data as a plain-text file. Each line is whether a bank-name or a offer-value.

3. Place text file under `test` folder.

4. Set paths and run `main.py`
