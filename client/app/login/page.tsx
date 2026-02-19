"use client";

import Link from "next/link";
import { useState } from "react";
import { AiOutlineEye, AiOutlineEyeInvisible } from "react-icons/ai";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <div className="w-full max-w-md p-8 bg-white dark:bg-zinc-900 rounded-lg shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-black dark:text-white mb-2">
            AirBall
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            Sign in to your account
          </p>
        </div>

        <form className="space-y-6">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-black dark:text-white mb-2"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-black dark:text-white mb-2"
            >
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                className="w-full px-4 py-2 pr-10 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-800 dark:text-zinc-800 cursor-pointer hover:text-black dark:hover:text-zinc-300 transition-colors"
              >
                {showPassword ? (
                  <AiOutlineEye size={20} />
                ) : (
                  <AiOutlineEyeInvisible size={20} />
                )}
              </button>
            </div>
            <div className="text-right mt-2">
              <button
                type="button"
                className="text-sm text-zinc-500 dark:text-zinc-500 hover:text-blue-700 dark:hover:text-white transition-colors cursor-pointer"
              >
                Forgot your password?
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium transition-colors"
          >
            Sign In
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-zinc-600 dark:text-zinc-400 text-sm">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="text-blue-600 dark:text-blue-400 font-medium hover:underline"
            >
              Sign up
            </Link>
          </p>
        </div>

        <div className="mt-4 text-center">
          <Link
            href="/"
            className="text-zinc-600 dark:text-zinc-400 text-sm hover:text-zinc-900 dark:hover:text-white"
          >
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
