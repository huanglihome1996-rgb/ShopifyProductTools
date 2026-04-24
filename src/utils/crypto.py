"""
加密工具
"""
from cryptography.fernet import Fernet
from src.config import settings


def _get_cipher() -> Fernet:
    """获取加密器"""
    key = settings.token_encryption_key or settings.secret_key
    # 确保密钥是有效的 Fernet 密钥（32字节 base64）
    if len(key) < 32:
        key = key.ljust(32, '0')
    key_bytes = key[:32].encode()
    # 使用简单的密钥派生
    import base64
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_token(token: str) -> str:
    """加密 token"""
    cipher = _get_cipher()
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """解密 token"""
    cipher = _get_cipher()
    return cipher.decrypt(encrypted_token.encode()).decode()
