#!/usr/bin/env python3
"""Aegis OS ISO Builder - Licensed Edition (requires license key)"""
from aegis_iso_builder import AegisISOBuilder

if __name__ == "__main__":
    app = AegisISOBuilder(licensed_mode=True)
    app.mainloop()
