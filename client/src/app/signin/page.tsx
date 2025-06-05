"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Eye, EyeOff, Mail,Lock, Trophy, ArrowLeft } from "lucide-react"
import axios from 'axios'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface FormData {
    email: string
    password: string
}

export default function SignUpPage() {
    const [formData, setFormData] = useState<FormData>({
        email: "",
        password: ""
    })

    const [showPassword, setShowPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target
        const fieldValue = type === "checkbox" ? checked : value

        setFormData((prev) => ({
            ...prev,
            [name]: fieldValue,
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (formData.email.trim() === "" || formData.password.trim() === "") {
            return
        }

        try{
            setIsLoading(true)

            const response = await axios.post("http://0.0.0.0:8000/api/users/login", {
                "email": formData.email,
                "password": formData.password
            })

            console.log(response)
        }
        catch (error) {
            console.error("error occured: ", e)
        }
        finally{
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex">
            <div className="hidden lg:flex lg:w-1/2 bg-black text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-red-600/20 to-black/80 z-10" />
                <div className="absolute inset-0 z-20 flex flex-col justify-center p-12">
                    <div className="flex items-center gap-3 mb-8">
                        <Trophy className="h-8 w-8 text-red-600" />
                        <span className="text-2xl font-bold">UFC Predictor</span>
                    </div>
                    <h1 className="text-5xl font-bold mb-4">Welcome Back!</h1>
                    <p className="text-xl text-gray-300 mb-8">
                        Jump back into using the prediction model, discuss your predictions, opinions and anything sports related with other MMA fans.
                    </p>
                </div>
            </div>

            <div className="w-full lg:w-1/2 flex items-center justify-center p-6">
                <div className="w-full max-w-md">
                    <div className="lg:hidden flex items-center gap-3 mb-8">
                        <Trophy className="h-6 w-6 text-red-600" />
                        <span className="text-xl font-bold">UFC Predictor</span>
                    </div>

                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to home
                    </Link>

                    <Card className="border-0 shadow-lg">
                        <CardHeader className="space-y-1 pb-2">
                            <CardTitle className="text-2xl font-bold">Sign in to your account</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Email field */}
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email address</Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="email"
                                            name="email"
                                            type="email"
                                            placeholder="john.doe@example.com"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className={`pl-10`}
                                        />
                                    </div>
                                </div>

                                {/* Password field */}
                                <div className="space-y-2">
                                    <Label htmlFor="password">Password</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="password"
                                            name="password"
                                            type={showPassword ? "text" : "password"}
                                            placeholder="Create a strong password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            className={`pl-10 pr-10`}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                                        >
                                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                        </button>
                                    </div>
                                </div>
                                <Button
                                    type="submit"
                                    className="w-full cursor-pointer bg-red-600 hover:bg-red-700"
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                             Signing in...
                                        </>
                                    ) : (
                                        "Sign in"
                                    )}
                                </Button>
                            </form>

                            <div className="text-center text-sm text-gray-600">
                                Don't have an account?{" "}
                                <Link href="/signup" className="text-red-600 hover:underline font-medium">
                                    Sign Up
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
