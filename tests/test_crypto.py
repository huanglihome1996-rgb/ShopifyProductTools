"""
加密工具测试
"""
import pytest
from src.utils.crypto import encrypt_token, decrypt_token


class TestCrypto:
    """加密工具测试类"""

    def test_encrypt_decrypt(self):
        """测试加密和解密"""
        original = "my_secret_token_12345"
        
        encrypted = encrypt_token(original)
        assert encrypted != original
        assert encrypted.startswith("enc:")  # 加密后的标识
        
        decrypted = decrypt_token(encrypted)
        assert decrypted == original

    def test_encrypt_different_tokens(self):
        """测试不同 token 加密结果不同"""
        token1 = "token_1"
        token2 = "token_2"
        
        encrypted1 = encrypt_token(token1)
        encrypted2 = encrypt_token(token2)
        
        assert encrypted1 != encrypted2

    def test_decrypt_invalid_token(self):
        """测试解密无效 token"""
        # 非加密字符串应该返回原值
        result = decrypt_token("plain_text")
        assert result == "plain_text"

    def test_encrypt_empty_token(self):
        """测试加密空 token"""
        encrypted = encrypt_token("")
        decrypted = decrypt_token(encrypted)
        assert decrypted == ""