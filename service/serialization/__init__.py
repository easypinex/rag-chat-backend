"""
Serialization 模組

提供 ConversionResult 的序列化和反序列化功能，支援 JSON 格式儲存和載入。
"""

from .conversion_serializer import ConversionSerializer
from .conversion_deserializer import ConversionDeserializer

__all__ = ['ConversionSerializer', 'ConversionDeserializer']
