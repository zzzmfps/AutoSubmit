# AutoSubmit

## Dependencies

 - requests
 - tqdm
 - PySide2 (required by GUI)

## Usage - CLI (Not recommended)
1. Set your account in `user.json` and place it under `assets/json` folder. The format must be:

    ```json
    [
        {
            "loginName": "<YOUR_USERNAME>",
            "loginPassword": "<YOUR_PASSWORD>",
            "loginTerminalType": 10,
            "isCarryOn": 1
        },
        {}
    ]
    ```

2. Recognize table data using Tencent QQ (Ctrl + Alt + O) or something else, save data as a plain-text file and place it under `test` folder. Each line is whether a bank-name or a offer-value.

## Usage - GUI (beta)

> Simple user interface. Instruction is not needed.
>
> Config `user.json` can be auto initialized and set. Still requires recognization tools.
