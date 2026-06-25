"""Tests for x402 payment protocol."""

import json

import pytest

from base_agent_toolkit.x402.payment import (
    PaymentHeader,
    PaymentRequirements,
)


class TestPaymentRequirements:
    """Tests for PaymentRequirements."""

    def test_from_headers(self):
        headers = {
            "X-PAYMENT": json.dumps({
                "scheme": "exact",
                "network": "base",
                "maxAmountRequired": "1000000000000000",
                "resource": "https://api.example.com/data",
                "payTo": "0x1234567890123456789012345678901234567890",
                "description": "API access",
            })
        }
        req = PaymentRequirements.from_response_headers(headers)
        assert req.scheme == "exact"
        assert req.network == "base"
        assert req.max_amount_required == 1_000_000_000_000_000
        assert "example.com" in req.resource

    def test_from_empty_headers(self):
        req = PaymentRequirements.from_response_headers({})
        assert req.scheme == "exact"
        assert req.max_amount_required == 0

    def test_amount_eth(self):
        req = PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=10**18,
            resource="https://test.com",
        )
        assert req.amount_eth == 1.0

    def test_small_amount(self):
        req = PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=10**15,
            resource="https://test.com",
        )
        assert abs(req.amount_eth - 0.001) < 1e-10


class TestPaymentHeader:
    """Tests for PaymentHeader."""

    def test_to_header_value(self):
        header = PaymentHeader(
            scheme="exact",
            network="base",
            payload={"amount": "1000", "resource": "https://test.com"},
            signature="0xabc123",
        )
        value = header.to_header_value()
        parsed = json.loads(value)
        assert parsed["scheme"] == "exact"
        assert parsed["network"] == "base"
        assert parsed["payload"]["amount"] == "1000"
        assert parsed["signature"] == "0xabc123"

    def test_as_dict(self):
        header = PaymentHeader(
            scheme="exact",
            network="base",
            payload={},
            signature="0x",
        )
        d = header.as_dict
        assert "X-PAYMENT" in d
        assert isinstance(d["X-PAYMENT"], str)
