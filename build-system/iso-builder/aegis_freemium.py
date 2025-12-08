#!/usr/bin/env python3
"""Aegis OS ISO Builder - Freemium Edition (auto-starts build)"""
from aegis_iso_builder import AegisISOBuilder

if __name__ == "__main__":
    app = AegisISOBuilder(licensed_mode=False)
    app.mainloop()
